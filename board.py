import pygame
import bot_exceptions
import robot
import sprite
import random

TYPE_FIELD, TYPE_WALL = 0, 1
MAX_TURNS = 60


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
        if not field.passable and bot is not None:
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
        print("teams", teams)
        return max(teams, key=teams.get)  # sort by values


class Board:

    def __init__(self, size, shape=(9, 9), robot_count=2, on_finish=None):
        self.shape = shape  # default 9 by 9
        print("shape", self.shape)
        self.size = size  # actual size in pixels
        self.on_finish = on_finish

        self.field_size = self.size[0] / 9, self.size[1] / 9
        obstacles = get_obstacles()

        # generate map
        self.map = Map([[Field(self.field_size,
                               kind=(TYPE_WALL if (row, col) in obstacles
                                     else TYPE_FIELD))
                         for col in range(self.shape[1])]
                        for row in range(self.shape[0])])

        # n robots
        ais = ["ai/test.py", "ai/other.py"]
        start_positions = [(2, 4, 0), (6, 4, 2)]
        self.bots = [robot.Robot(self.field_size, team, self.map,
                                 self.game_over,
                                 start_positions[team][:-1],
                                 start_positions[team][-1],
                                 ais[team],)
                     for team in range(robot_count)]
        random.shuffle(self.bots)
        self.__itbots = self._iter_bots()  # initialize bot generator
        self.turns = 0
        self.is_playing = False

    def draw(self):
        surf = pygame.Surface(self.size)
        surf.fill((0, 0, 0))

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

    def game_over(self, winner=None):
        if winner:
            print("The game is over: Team {0} has won!".format(winner.team))
        else:
            print("The game is over!")
        if self.on_finish:
            self.on_finish()

    def on_turn(self):
        if not self.is_playing:
            return
        bot = self.next_bot()
        bot.on_turn(MAX_TURNS - self.turns)
        self.turns += 1
        if self.turns >= MAX_TURNS:
            # get winner: team with most fields
            team = self.map.get_most_team()
            print("team with most fields", team)
            try:
                bot = [b for b in self.bots if b.team == team][0]
            except KeyError:
                self.game_over()
            else:
                self.game_over(winner=bot)

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


class Field(sprite.Sprite):

    wall_image = None

    def __init__(self, size, kind=TYPE_FIELD, team=None):
        super(Field, self).__init__(size)
        self.kind = kind
        self.entity = None
        self.team = None
        if not Field.wall_image:
            Field.wall_image = \
                pygame.transform.scale(pygame.image.load("wall.png"),
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
    def passable(self):
        return self.kind != TYPE_WALL and self.entity is None

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
