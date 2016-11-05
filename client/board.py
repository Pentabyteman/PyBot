#!/usr/bin/python
# -*- coding: iso-8859-15 -*-"

import pygame
import robot
import sprite

TYPE_FIELD, TYPE_WALL = 0, 1
MAX_TURNS = 180


class Map:

    def __init__(self, fields):
        self.fields = fields

    def move(self, bot, row, col):
        try:
            if self.get(bot.row, bot.col) == bot:
                self.set(None, bot.row, bot.col)  # clear old field
        except AttributeError:  # when not initialized, in the beginning
            pass
        self.set(bot, row, col)  # move to new

    def get(self, row, col):
        return self.fields[row][col].entity

    def set(self, bot, row, col):
        field = self.fields[row][col]
        field.entity = bot

    def get_fields(self):
        for row in self.fields:
            for field in row:
                yield field


class Board:

    def __init__(self, size, initial=None):
        self.size = size  # actual size in pixels

        self.__speakers = None  # to play sounds

        self.field_size = self.size[0] / 9, self.size[1] / 9

        # generate map
        self.map = None
        if initial is not None:
            self.set_initial(initial)

    def draw(self):
        surf = pygame.Surface(self.size)
        surf.fill((0, 0, 0))
        if self.map is None:
            return surf

        # draw grid as background
        for row, _ in enumerate(self.map.fields):
            for col, _ in enumerate(_):
                w, h = self.field_size
                rect = pygame.Rect(col * w, row * h, w, h)
                pygame.draw.rect(surf, (255, 255, 255), rect, 1)

        # draw fields on top of it
        for row, _ in enumerate(self.map.fields):
            for col, field in enumerate(_):
                x, y = col * self.field_size[0], row * self.field_size[1]
                surf.blit(field.image, (x, y))
        return surf

    def on_event(self, event=None):
        pass

    def on_tick(self):
        if self.map is None or not hasattr(self, "bots"):
            return
        for bot in self.bots:
            bot.on_tick()

    @property
    def speakers(self):
        return self.__speakers

    @speakers.setter
    def speakers(self, new):
        self.__speakers = new
        if self.map is None:
            return
        for bot in self.bots:
            bot.speakers = new

    def set_initial(self, initial):
        self.map = Map([[Field(self.field_size, kind, team)
                         for kind, team in row]
                        for row in initial["map"]])

        # n robots
        bot_info = initial["bots"]
        self.bots = [robot.Robot(self.field_size, team, self.map,
                                 bot_info[team]["pos"],
                                 bot_info[team]["rot"],)
                     for team in range(len(bot_info))]
        for bot in self.bots:
            bot.speakers = self.speakers  # add speakers to the robots
        print("initialized map")

    def update(self, update):
        for bot in self.bots:
            # TODO: Update gamelog properly @Pentabyteman
            bot.pos = update[bot.team]["pos"]
            bot.rotation = update[bot.team]["rot"]
            bot.action(update[bot.team]["move"])
            bot.health = update[bot.team]["health"]


class Field(sprite.Sprite):

    wall_image = None

    def __init__(self, size, kind=TYPE_FIELD, team=None):
        super(Field, self).__init__(size)
        self.kind = kind
        self.entity = None
        self.team = None
        if not Field.wall_image:
            Field.wall_image = \
                pygame.transform.scale(pygame.image.load("resources/wall.png"),
                                       self.size)

    def __repr__(self):
        return "Field [{kind}]".format(kind="Field" if self.kind == TYPE_FIELD
                                       else "Wall")

    def draw(self):
        self.draw_background()
        if self.entity:
            self.surface.blit(self.entity.image, (0, 0))

    @property
    def entity(self):
        return self.__entity

    @entity.setter
    def entity(self, new):
        self.__entity = new
        if new is not None:
            self.team = new.team
        self.state = sprite.Sprite.STATE_INVALID

    @property
    def image(self):
        if self.state == Field.STATE_INVALID or\
                (self.entity is not None and
                 self.entity.state == Field.STATE_INVALID):
            self.draw()
            self.state = Field.STATE_VALID
        return self.surface

    def draw_background(self):
        if self.kind == TYPE_FIELD:
            self.surface.fill((0, 0, 0, 0)) if self.team is None else\
                self.surface.fill(robot.team_color(self.team, alpha=100))
        elif self.kind == TYPE_WALL:
            self.surface.blit(self.wall_image, (0, 0))
