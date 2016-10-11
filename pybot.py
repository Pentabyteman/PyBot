import pygame
import board
from app import App


WINDOW_SIZE = (1017, 1017)  # quadratisch praktisch gut


class Game(App):

    def __init__(self, display):
        super(Game, self).__init__()
        self.display = display

        self.board = board.Board(self.display.get_size())

    def on_event(self, event):
        self.board.on_event(event)

    def on_tick(self):
        self.board.on_turn()

    def on_render(self):
        self.display.fill((255, 255, 255))
        self.display.blit(self.board.draw(), (0, 0))  # blit board
        pygame.display.flip()  # update screen


if __name__ == '__main__':

    pygame.init()
    display = pygame.display.set_mode(WINDOW_SIZE)  # setup display
    game = Game(display)
    game.exec_()
