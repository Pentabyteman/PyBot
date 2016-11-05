#!/usr/bin/python
# -*- coding: iso-8859-15 -*-"

import bot_exceptions
import robot
import random

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
        if (not field.passable and bot is not None) or row < 0 or col < 0:
            raise bot_exceptions.IllegalMoveException("Field not passable")
        field.entity = bot

    def get_fields(self):
        for row in self.fields:
            for field in row:
                yield field

    def get_most_team(self):
        teams = {}
        for field in self.get_fields():
            if field.team is None:
                continue
            if field.team not in teams:
                teams[field.team] = 1
            else:
                teams[field.team] += 1
        return max(teams, key=teams.get)  # sort by values

    def compress(self):
        width, height = len(self.fields[0]), len(self.fields)
        res = [[None for _ in range(width)] for _ in range(height)]
        for row, _ in enumerate(self.fields):
            for col, field in enumerate(_):
                res[row][col] = (field.kind, field.team)
        return res


class Board:

    def __init__(self, shape=(9, 9), on_finish=None,
                 start=None):
        self.shape = shape  # default 9 by 9
        self.on_finish = on_finish

        obstacles = get_obstacles()

        # generate map
        self.map = Map([[Field(
                               kind=(TYPE_WALL if (row, col) in obstacles
                                     else TYPE_FIELD))
                         for col in range(self.shape[1])]
                        for row in range(self.shape[0])])

        # n robots
        start_positions = [(2, 4, 0), (6, 4, 2)]
        self.bots = [robot.Robot(team, self.map,
                                 self.game_over,
                                 start_positions[team][:-1],
                                 start_positions[team][-1])
                     for team in range(2)]
        if start == 1:
            self.bots.reverse()
        elif start is None:
            random.shuffle(self.bots)
        self.__itbots = self._iter_bots()  # initialize bot generator
        self.turns = 0
        self.is_playing = False

    def on_event(self, event=None):
        pass

    def game_over(self, winner=None, loser=None):
        if loser is not None:
            winner = [b for b in self.bots if b != loser][0]
        if winner is None:
            print("The game is over!")
        else:
            print("The game is over: Team {0} has won!".format(winner.team))
        if self.on_finish:
            self.on_finish()

    def start_game(self, ais):
        if self.is_playing:
            return
        for bot, ai in zip(sorted(self.bots, key=lambda x: x.team),
                           ais):
            bot.ai = ai
        self.is_playing = True
        return self.map

    def on_turn(self):
        if not self.is_playing:
            return
        bot = self.next_bot()
        change = {}
        move = bot.on_turn(MAX_TURNS - self.turns)  # e.g: move or attack
        change[bot.team] = move
        if move == "attack":
            change[int(not bot.team)] = "hit"
        else:
            change[int(not bot.team)] = None

        self.turns += 1
        if self.turns >= MAX_TURNS:
            # get winner: team with most fields
            team = self.map.get_most_team()
            try:
                bot = [b for b in self.bots if b.team == team][0]
            except KeyError:
                self.game_over()
            else:
                self.game_over(winner=bot)
        return {b.team: b.serialize(change[b.team]) for b in self.bots}

    def on_tick(self):
        for bot in self.bots:
            bot.on_tick()

    def next_bot(self):
        if not self.__itbots:
            self.__itbots = self._iter_bots()
        return self.__itbots.__next__()

    def _iter_bots(self):
        idx = 0
        while True:
            yield self.bots[idx]
            if idx + 1 >= len(self.bots):
                idx = 0
            else:
                idx += 1


class Field():

    def __init__(self, kind=TYPE_FIELD, team=None):
        self.kind = kind
        self.entity = None
        self.team = None

    def __repr__(self):
        return "Field [{kind}]".format(kind="Field" if self.kind == TYPE_FIELD
                                       else "Wall")

    @property
    def entity(self):
        return self.__entity

    @entity.setter
    def entity(self, new):
        self.__entity = new
        if new is not None:
            self.team = new.team

    @property
    def passable(self):
        return self.kind != TYPE_WALL and self.entity is None


def get_obstacles():
    List_Normal1 = [[1, 1, 1, 1, 1, 1, 1, 2, 2, 3, 3, 3, 3, 4, 4], [
        1, 2, 3, 4, 5, 6, 7, 1, 7, 1, 3, 5, 7, 1, 3]]
    List_Spiegel1 = [[7, 7, 7, 7, 7, 7, 7, 6, 6, 5, 5, 5, 5, 4, 4], [
        7, 6, 5, 4, 3, 2, 1, 7, 1, 7, 5, 3, 1, 7, 5]]
    List_Normal2 = [[1, 1, 1, 1, 1, 1, 1, 2, 2, 3, 3, 3, 3, 4, 4], [
        1, 2, 3, 4, 5, 6, 7, 1, 7, 1, 3, 5, 7, 1, 3]]
    List_Spiegel2 = [[7, 7, 7, 7, 7, 7, 7, 6, 6, 5, 5, 5, 5, 4, 4], [
        7, 6, 5, 4, 3, 2, 1, 7, 1, 7, 5, 3, 1, 7, 5]]
    x = random.randint(0, 14)
    while True:
        y = random.randint(0, 14)
        if x != y:
            break
    obstacle1 = (List_Normal1[0][x], List_Normal1[1][x])
    obstacle2 = (List_Spiegel1[0][x], List_Spiegel1[1][x])
    obstacle3 = (List_Normal2[0][y], List_Normal2[1][y])
    obstacle4 = (List_Spiegel2[0][y], List_Spiegel2[1][y])
    return obstacle1, obstacle2, obstacle3, obstacle4
