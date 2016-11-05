#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

from bot_exceptions import IllegalMoveException, InvalidAiException
import importlib.util as imputil

DIRECTIONS = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # north, east, south, west
COLORS = [(255, 0, 0), (0, 0, 255), (0, 255, 0), (255, 0, 255)]
ROTATE_RIGHT, ROTATE_LEFT = 1, -1
MOVE_FORWARD, MOVE_BACK = 0, -1

# how much hp an attack from the given side deals
FROM_BEHIND, FROM_SIDE, FROM_FRONT = 0, 1, 2
DAMAGE = {FROM_BEHIND: 50, FROM_SIDE: 30, FROM_FRONT: 10}


class Robot():

    def __init__(self, team, map, game_over, pos=(0, 0),
                 rotation=0):
        self.team = team
        self.map = map
        self.game_over = game_over
        self.first_turn = True

        self.maxhealth = 100
        self.health = self.maxhealth
        self.rotation = rotation
        try:
            self.pos = pos
        except IllegalMoveException:
            print("Not a valid position")

    def __repr__(self):
        try:
            pos = self.pos
        except AttributeError:
            pos = (-1, -1)
        return "Robot[{pos}] {team}".format(pos=pos, team=self.team)

    def serialize(self, move=-1):
        info = {"pos": self.pos, "rot": self.rotation, "health": self.health}
        if move != -1:
            info["move"] = move
        return info

    def rotate(self, direction):
        """
        Rotates the robot in the given direction

        Arguments:
        direction -- 1 := 90 degrees, -1 := -90 degrees
        """
        self.rotation += min(max(direction, -1), 1)
        if self.rotation >= 4:
            self.rotation = 0
        elif self.rotation <= -1:
            self.rotation = 3

    def move(self, direction, proportional=False):
        """
        Moves the robot in the specified direction

        Arguments:
        direction -- Direction of momement in the perspective of the robot's
                     current rotation.
        """
        # validity of direction
        if not proportional:
            assert direction != 0 and -1 <= direction <= 1, "No valid movement"
        # p: eigene position, d * (vorne/hinten): positionsänderung
        self.pos = [p + (d * direction)
                    for p, d in zip(self.pos, DIRECTIONS[self.rotation])]

    def attack(self, direction):
        """Attacks in the specified direction -> move"""
        # validity of direction
        assert 0 <= direction <= 1, "No valid attack"
        front_pos = \
            [p + d
             for p, d in zip(self.pos, DIRECTIONS[self.rotation])]
        other = self.map.get(*front_pos)
        assert other is not None, "No robot to attack!"
        self.hit(other, push=direction == 1)

    def hit(self, other=None, push=False):
        """Attacks the robot in front of self"""
        if not other:
            front_pos = \
                [p + d for p, d in zip(self.pos, DIRECTIONS[self.rotation])]
            other = self.map.get(front_pos)
        assert other is not None, "No robot in front!"
        if push:
            other.pos = [p + d for p, d in
                         zip(other.pos, DIRECTIONS[self.rotation])]
        # get the hit direction
        look_other = DIRECTIONS[other.rotation]
        look_self = DIRECTIONS[self.rotation]
        if look_other == look_self:  # von hinten getroffen
            damage = DAMAGE[FROM_BEHIND]
        elif all(abs(x) != abs(y)
                 for x, y in zip(look_other, look_self)):  # seitlich
            damage = DAMAGE[FROM_SIDE]
        else:  # frontal
            damage = DAMAGE[FROM_FRONT]

        other.health -= damage if not push else damage * 0.25

    def on_turn(self, turns_to_go):
        if self.first_turn:
            pos, rot = self.pos, self.rotation
            self.first_turn = False
        else:
            pos, rot = None, None
        try:
            move = self.ai.get_action(self.ask_for_field,
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
            return cmd
        except Exception as e:
            print("The AI of team {0} failed to answer!".format(self.team), e)
            self.game_over(loser=self)
            return "failed"

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

    @property
    def health(self):
        return self.__health

    @health.setter
    def health(self, new):
        self.__health = max(new, 0)
        if self.__health <= 0:
            self.game_over(loser=self)

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