import pygame
from os.path import join
import time
import glob
from bot_exceptions import IllegalMoveException, InvalidAiException
import sprite
import importlib.util as imputil

DIRECTIONS = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # north, east, south, west
COLORS = [(255, 0, 0), (0, 0, 255), (0, 255, 0), (255, 0, 255)]
IMAGE_PATHS = ["resources/animation_red/robot_red_normal.png",
               "resources/animation_blue/blue_robot_normal.png"]
ANIMATION_DIR = ["resources/animation_red",
                 "resources/animation_blue"]
BOT_IMAGES = [pygame.image.load(f) for f in IMAGE_PATHS]
ROTATE_RIGHT, ROTATE_LEFT = 1, -1
MOVE_FORWARD, MOVE_BACK = 0, -1

# how much hp an attack from the given side deals
FROM_BEHIND, FROM_SIDE, FROM_FRONT = 0, 1, 2
DAMAGE = {FROM_BEHIND: 50, FROM_SIDE: 30, FROM_FRONT: 10}
AI_PATH = "ai/test.py"  # default ai


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

    def __init__(self, size, team, map, game_over, pos=(0, 0),
                 rotation=0, ai_path=AI_PATH):
        super(Robot, self).__init__(size)
        self.team = team
        self.map = map
        self.game_over = game_over
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
        self.gamelog_callbacks = []
        self.maxhealth = 100
        self.health = self.maxhealth
        self.rotation = rotation
        try:
            self.pos = pos
        except IllegalMoveException:
            print("Not a valid position")

        # load ai module
        self.ai = ai_path

    def __repr__(self):
        try:
            pos = self.pos
        except AttributeError:
            pos = (-1, -1)
        return "Robot[{pos}] {team}".format(pos=pos, team=self.team)

    def rotate(self, direction):
        """
        Rotates the robot in the given direction

        Arguments:
        direction -- 1 := 90 degrees, -1 := -90 degrees
        """
        electro = pygame.mixer.Sound('resources/Electro_Motor.wav')
        electro.set_volume(0.2)
        self.rotation += min(max(direction, -1), 1)
        if self.rotation >= 3:
            self.rotation = 0
        elif self.rotation <= -1:
            self.rotation = 3
        if self.speakers:
            print("playing electro")
            self.speakers.play(electro)
        new_turn = "r={}".format(self.rotation)
        self._call_gamelog_callbacks(new_turn)

    def move(self, direction, proportional=False):
        """
        Moves the robot in the specified direction

        Arguments:
        direction -- Direction of momement in the perspective of the robot's
                     current rotation.
        """
        servo = pygame.mixer.Sound(file='resources/Servo_Motor.wav')
        servo.set_volume(0.2)
        # validity of direction
        if not proportional:
            assert direction != 0 and -1 <= direction <= 1, "No valid movement"
        # p: eigene position, d * (vorne/hinten): positionsänderung
        self.pos = [p + (d * direction)
                    for p, d in zip(self.pos, DIRECTIONS[self.rotation])]
        if self.speakers:
            self.speakers.play(servo)
        new_turn = "{0}".format(self.pos)
        self._call_gamelog_callbacks(new_turn)

    def attack(self, direction):
        """Attacks in the specified direction -> move"""
        # validity of direction
        assert -2 <= direction <= 2, "No valid attack"
        add = 1 if direction >= 0 else -1
        front_pos = \
            [p + d * (direction + add)
             for p, d in zip(self.pos, DIRECTIONS[self.rotation])]
        other = self.map.get(*front_pos)
        assert other is not None, "No robot to attack!"
        if direction != 0:
            self.move(direction, proportional=True)
        self.hit(other)
        if hasattr(self, 'attack_anim'):
            self.animator.play_animation(self.attack_anim)

    def hit(self, other=None):
        """Attacks the robot in front of self"""
        laser = pygame.mixer.Sound('resources/Laser.wav')
        laser.set_volume(0.5)
        if not other:
            front_pos = \
                [p + d for p, d in zip(self.pos, DIRECTIONS[self.rotation])]
            other = self.map.get(front_pos)
        assert other is not None, "No robot in front!"
        look_other = DIRECTIONS[other.rotation]
        look_self = DIRECTIONS[self.rotation]
        print(self, "hits", other)
        if look_other == look_self:  # von hinten getroffen
            other.health -= DAMAGE[FROM_BEHIND]
            damage = DAMAGE[FROM_BEHIND]
        elif all(abs(x) != abs(y)
                 for x, y in zip(look_other, look_self)):  # seitlich
            other.health -= DAMAGE[FROM_SIDE]
            damage = DAMAGE[FROM_SIDE]
        else:  # frontal
            other.health -= DAMAGE[FROM_FRONT]
            damage = DAMAGE[FROM_FRONT]
        if hasattr(other, 'take_damage_anim'):
            other.animator.play_animation(other.take_damage_anim)
        if self.speakers:
            self.speakers.play(laser)
        new_turn = "{0}!{1};{2}".format(self.pos, other.pos, damage)
        self._call_gamelog_callbacks(new_turn)

    def draw(self):
        img = pygame.transform.scale(self.animator.image, self.size)
        img = pygame.transform.rotate(img, self.rotation * -90)
        self.surface.blit(img, (0, 0))

    def team_color(self, alpha=255):
        return COLORS[self.team] + (alpha,)

    def on_turn(self, turns_to_go):
        if self.first_turn:
            pos, rot = self.pos, self.rotation
            self.first_turn = False
        else:
            pos, rot = None, None
        try:
            move = self.ai.get_move(self.ask_for_field,
                                    turns_to_go,
                                    position=pos,
                                    rotation=rot)
            cmd, arg = move.split(" ")
            if cmd == "move":
                self.move(int(arg))
            elif cmd == "rotate":
                self.rotate(int(arg))
            elif cmd == "attack":
                self.attack(int(arg))
        except Exception as e:
            print("The AI failed to answer!", e)
            self.game_over()

    def on_tick(self):
        result = self.animator.on_tick()
        if result == Robot.STATE_INVALID:
            self.state = Robot.STATE_INVALID

    def ask_for_field(self, row, col):
        """Returns a limited amount of information about a specific field"""
        field = self.map.fields[row][col]
        # return the field kind, team, and if there is an entity or not
        return field.passable, field.team, field.entity is not None

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
        print("rotated -> redraw")

    @property
    def health(self):
        return self.__health

    @health.setter
    def health(self, new):
        self.__health = max(new, 0)
        self._call_health_callbacks(self.__health)
        print(self, "has now", self.__health, "hp")
        if self.__health <= 0:
            self.game_over()

    def register_health_callback(self, func):
        self.health_callbacks.append(func)
        func(self.health)

    def _call_health_callbacks(self, health):
        for func in self.health_callbacks:
            func(health)

    def register_gamelog_callback(self, func):
        self.gamelog_callbacks.append(func)

    def _call_gamelog_callbacks(self, new_turn):
        for func in self.gamelog_callbacks:
            func(new_turn)

    @property
    def ai(self):
        return self.__ai

    @ai.setter
    def ai(self, ai_path):
        try:
            ai_name = ai_path.split("/")[-1].split(".")[0]
            spec = imputil.spec_from_file_location(ai_name, ai_path)
            self.__ai = imputil.module_from_spec(spec)
            spec.loader.exec_module(self.__ai)
        except AttributeError:
            raise InvalidAiException


def team_color(team, alpha=255):
    return COLORS[team] + (alpha,)


def bot_image(team):
    return pygame.image.load(IMAGE_PATHS[team])
