import pygame


class Sprite:

    STATE_VALID, STATE_INVALID = 0, 1

    def __init__(self, size):
        self.size = size
        self.surface = pygame.Surface(self.size, pygame.SRCALPHA)
        self.state = Sprite.STATE_INVALID

    @property
    def image(self):
        if self.state == Sprite.STATE_INVALID:
            self.draw()
            self.state = Sprite.STATE_VALID

        return self.surface
