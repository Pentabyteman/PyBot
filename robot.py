import pygame
from bot_exceptions import IllegalMoveException
import sprite
import importlib.util as imputil

AI_PATH = "ai/test.py"
DIRECTIONS = [(1, 0), (0, 1), (-1, 0), (0, -1)]  # 0 = N, 1 = S, etc.
COLORS = [(255, 0, 0), (0, 0, 255), (0, 255, 0), (255, 0, 255)]
IMAGE_PATHS = ["robot_red.png", "robot_blue.png"]
BOT_IMAGES = [pygame.image.load(f) for f in IMAGE_PATHS]
ROTATE_RIGHT, ROTATE_LEFT = 1, -1
MOVE_FORWARD, MOVE_BACK, MOVE_LEFT, MOVE_RIGHT = 0, 2, 3, 1


class Robot(sprite.Sprite):

    def __init__(self, size, team, map, game_over, pos=(0, 0),
                 ai_path=AI_PATH):
        super(Robot, self).__init__(size)
        self.team = team
        self.map = map
        self.game_over = game_over

        self.maxhealth = 100
        self.health = self.maxhealth
        self.rotation = 0
        try:
            self.pos = pos
        except IllegalMoveException:
            print("Not a valid position")

        # load ai module
        ai_name = ai_path.split("/")[-1].split(".")[0]
        spec = imputil.spec_from_file_location(ai_name, ai_path)
        self.ai = imputil.module_from_spec(spec)
        spec.loader.exec_module(self.ai)

        # test
        self.move(MOVE_FORWARD)
        self.rotate(ROTATE_LEFT)

    def __repr__(self):
        try:
            pos = self.pos
        except AttributeError:
            pos = (-1, -1)
        return "Robot[{pos}] {team}".format(pos=pos, team=self.team)

    def move(self, direction):
        self.pos = [p + d for p, d in zip(self.pos, DIRECTIONS[direction])]

    def draw(self):
        img = pygame.transform.scale(bot_image(self.team), self.size)
        img = pygame.transform.rotate(img, self.rotation)
        self.surface.blit(img, (0, 0))

    def team_color(self, alpha=255):
        return COLORS[self.team] + (alpha,)

    def on_turn(self):
        move = self.ai.get_move()
        try:
            cmd, arg = move.split(" ")
            if cmd == "move":
                self.move(int(arg))
            elif cmd == "rotate":
                self.move(int(arg))
        except Exception:
            print("The AI failed to answer!")
            self.game_over()

    def rotate(self, direction):
        """
        Rotates the robot in the given direction

        Arguments:
        direction -- 1 := 90 degrees, -1 := -90 degrees
        """
        self.rotation += min(max(direction, -1), 1) * -90

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
        if self.__health <= 0:
            self.game_over()


def team_color(team, alpha=255):
    return COLORS[team] + (alpha,)


def bot_image(team):
    return pygame.image.load(IMAGE_PATHS[team])
