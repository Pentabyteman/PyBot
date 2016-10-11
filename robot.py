import pygame
from bot_exceptions import IllegalMoveException
import sprite
import importlib.util as imputil

AI_PATH = "ai/test.py"


class Robot(sprite.Sprite):

    def __init__(self, size, team, map, pos=(0, 0), ai_path=AI_PATH):
        super(Robot, self).__init__(size)
        self.team = team
        self.map = map
        self.max_health = 100
        self.__health = self.max_health
        try:
            print("pos", pos)
            self.pos = pos
        except IllegalMoveException:
            print("Not a valid position")

        # load ai module
        ai_name = ai_path.split("/")[-1].split(".")[0]
        spec = imputil.spec_from_file_location(ai_name, ai_path)
        self.ai = imputil.module_from_spec(spec)
        spec.loader.exec_module(self.ai)

    def draw(self):
        pygame.draw.ellipse(self.surface, (255, 0, 0), self.surface.get_rect())

    def on_turn(self):
        print(self.ai.get_move())

    @property
    def pos(self):
        return (self.__row, self.__col)

    @pos.setter
    def pos(self, pos):
        row, col = pos
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
    def health(self):
        pass

    @health.setter
    def health(self, new):
        self.__health = new
        if self.__health <= 0:
            # send gameover
            pass
