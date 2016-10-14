import pygame
from bot_exceptions import IllegalMoveException
import sprite
import importlib.util as imputil

AI_PATH = "ai/test.py"
DIRECTIONS = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # north, east, south, west
COLORS = [(255, 0, 0), (0, 0, 255), (0, 255, 0), (255, 0, 255)]
IMAGE_PATHS = ["robot_red.png", "robot_blue.png"]
BOT_IMAGES = [pygame.image.load(f) for f in IMAGE_PATHS]
ROTATE_RIGHT, ROTATE_LEFT = 1, -1
MOVE_FORWARD, MOVE_BACK = 0, -1

# how much hp an attack from the given side deals
FROM_BEHIND, FROM_SIDE, FROM_FRONT = 0, 1, 2
DAMAGE = {FROM_BEHIND: 50, FROM_SIDE: 30, FROM_FRONT: 10}


class Robot(sprite.Sprite):

    def __init__(self, size, team, map, game_over, pos=(0, 0),
                 rotation=0, ai_path=AI_PATH):
        super(Robot, self).__init__(size)
        self.team = team
        self.map = map
        self.game_over = game_over

        self.maxhealth = 100
        self.health = self.maxhealth
        self.rotation = rotation
        try:
            self.pos = pos
        except IllegalMoveException:
            print("Not a valid position")

        # load ai module
        ai_name = ai_path.split("/")[-1].split(".")[0]
        spec = imputil.spec_from_file_location(ai_name, ai_path)
        self.ai = imputil.module_from_spec(spec)
        spec.loader.exec_module(self.ai)

    def __repr__(self):
        try:
            pos = self.pos
        except AttributeError:
            pos = (-1, -1)
        return "Robot[{pos}] {team}".format(pos=pos, team=self.team)

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
        assert -2 <= direction <= 2, "No valid attack"
        add = 1 if direction >= 0 else -1
        front_pos = \
            [p + d * (direction + add)
             for p, d in zip(self.pos, DIRECTIONS[self.rotation])]
        other = self.map.get(*front_pos)
        assert other is not None, "No robot to attack!"
        self.move(direction, proportional=True)
        self.hit(other)

    def hit(self, other=None):
        """Attacks the robot in front of self"""
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
        elif all(abs(x) != abs(y)
                 for x, y in zip(look_other, look_self)):  # seitlich
            other.health -= DAMAGE[FROM_SIDE]
        else:  # frontal
            other.health -= DAMAGE[FROM_FRONT]

    def draw(self):
        img = pygame.transform.scale(bot_image(self.team), self.size)
        img = pygame.transform.rotate(img, self.rotation * -90)
        self.surface.blit(img, (0, 0))

    def team_color(self, alpha=255):
        return COLORS[self.team] + (alpha,)

    def on_turn(self):
        move = self.ai.get_move()
        # try:
        cmd, arg = move.split(" ")
        if cmd == "move":
            self.move(int(arg))
        elif cmd == "rotate":
            self.rotate(int(arg))
        elif cmd == "attack":
            self.attack(int(arg))
        # except Exception as e:
            # print("The AI failed to answer!", e)
            # self.game_over()

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
            self.rotation = 4

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
        self.__health = new
        print(self, "has now", new, "hp")
        if self.__health <= 0:
            self.game_over()


def team_color(team, alpha=255):
    return COLORS[team] + (alpha,)


def bot_image(team):
    return pygame.image.load(IMAGE_PATHS[team])
