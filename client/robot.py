#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

import pygame
from os.path import join
import time
import glob
import sprite

DIRECTIONS = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # north, east, south, west
COLORS = [(255, 0, 0), (0, 0, 255), (0, 255, 0), (255, 0, 255)]
IMAGE_PATHS = ["resources/animation_red/robot_red_normal.png",
               "resources/animation_blue/blue_robot_normal.png"]
ANIMATION_DIR = ["resources/animation_red",
                 "resources/animation_blue"]
BOT_IMAGES = [pygame.image.load(f) for f in IMAGE_PATHS]
ROTATE_RIGHT, ROTATE_LEFT = 1, -1
MOVE_FORWARD, MOVE_BACK = 0, -1


class Animation:

    def __init__(self, images, length):
        self.images = images
        self.length = length
        self.image_duration = self.length / len(self.images)
        self.frame = 0
        self.last_time = 0

    @property
    def image(self):
        return self.images[self.frame]

    def on_tick(self):
        # increases frame until last frame reached
        if time.time() > self.last_time + self.image_duration:
            if self.frame < len(self.images) - 1:
                self.frame += 1
            else:
                self.on_finish()
            self.last_time = time.time()

    def on_finish(self):
        pass

    @staticmethod
    def from_path(pattern, length):
        img_files = glob.glob(pattern)
        images = [pygame.image.load(path) for path in sorted(img_files)]
        return Animation(images, length)


class Animator:

    def __init__(self, default_image):
        self.current_animation = None
        self.default_image = default_image

    def play_animation(self, animation):
        animation.frame = 0
        animation.on_finish = self.stop_animation
        self.current_animation = animation

    def stop_animation(self):
        self.current_animation = None

    @property
    def image(self):
        if self.current_animation is not None:
            return self.current_animation.image
        else:
            return self.default_image

    def on_tick(self):
        if self.current_animation is not None:
            self.current_animation.on_tick()
            return Robot.STATE_INVALID
        return Robot.STATE_VALID


class Robot(sprite.Sprite):

    def __init__(self, size, team, map, pos=(0, 0),
                 rotation=0):
        super(Robot, self).__init__(size)
        self.team = team
        self.map = map
        self.first_turn = True

        default_img = IMAGE_PATHS[self.team]
        self.animator = Animator(pygame.image.load(default_img))
        anim_dir = ANIMATION_DIR[self.team]
        if anim_dir is not None:
            self.take_damage_anim = \
                Animation.from_path(join(anim_dir, '*_robot_take_damage*'), 1)
            self.attack_anim = Animation.from_path(join(anim_dir,
                                                   '*_robot_attack_*'), 0.5)

        self.speakers = None  # speakers to play sounds

        self.health_callbacks = []
        self.maxhealth = 100
        self.health = self.maxhealth
        self.rotation = rotation
        self.pos = pos

    def __repr__(self):
        try:
            pos = self.pos
        except AttributeError:
            pos = (-1, -1)
        return "Robot[{pos}] {team}".format(pos=pos, team=self.team)

    def action(self, action):
        if action == "rotate":
            self.rotate()
        elif action == "move":
            self.move()
        elif action == "attack":
            self.attack()
        elif action == "hit":
            self.hit()

    def rotate(self):
        """Rotates the robot in the given direction"""
        electro = pygame.mixer.Sound('resources/Electro_Motor.wav')
        electro.set_volume(0.2)
        if self.speakers:
            self.speakers.play(electro)

    def move(self):
        """Moves the robot in the specified direction"""
        servo = pygame.mixer.Sound(file='resources/Servo_Motor.wav')
        servo.set_volume(0.2)
        if self.speakers:
            self.speakers.play(servo)

    def attack(self):
        """Attacks in the specified direction -> move"""
        laser = pygame.mixer.Sound('resources/Laser.wav')
        laser.set_volume(0.5)
        if hasattr(self, 'attack_anim'):
            self.animator.play_animation(self.attack_anim)
        if self.speakers:
            self.speakers.play(laser)

    def hit(self, other=None):
        """Hits the robot"""
        if hasattr(self, 'take_damage_anim'):
            self.animator.play_animation(self.take_damage_anim)

    def draw(self):
        img = pygame.transform.scale(self.animator.image, self.size)
        img = pygame.transform.rotate(img, self.rotation * -90)
        self.surface.blit(img, (0, 0))

    def team_color(self, alpha=255):
        return COLORS[self.team] + (alpha,)

    def on_tick(self):
        result = self.animator.on_tick()
        if result == Robot.STATE_INVALID:
            self.state = Robot.STATE_INVALID

    @property
    def pos(self):
        return (self.__row, self.__col)

    @pos.setter
    def pos(self, pos):
        self.map.move(self, *pos)
        self.__row, self.__col = pos

    @property
    def row(self):
        return self.__row

    @row.setter
    def row(self, row):
        self.map.move(self, row, self.col)
        self.__row = row

    @property
    def col(self):
        return self.__col

    @col.setter
    def col(self, col):
        self.map.move(self, col, self.row)
        self.__col = col

    @property
    def rotation(self):
        return self.__rotation

    @rotation.setter
    def rotation(self, new):
        self.__rotation = new
        self.state = Robot.STATE_INVALID

    @property
    def health(self):
        return self.__health

    @health.setter
    def health(self, new):
        self.__health = max(new, 0)
        self._call_health_callbacks(self.health)

    def register_health_callback(self, callback):
        self.health_callbacks.append(callback)
        callback(self.health)

    def _call_health_callbacks(self, health):
        for callback in self.health_callbacks:
            callback(health)


def team_color(team, alpha=255):
    return COLORS[team] + (alpha,)


def bot_image(team):
    return pygame.image.load(IMAGE_PATHS[team])