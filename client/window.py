import pygame
from ui_components import UIGroup


class Window:

    STATE_VALID, STATE_INVALID = 1, 0

    def __init__(self, size):
        self.size = size
        self.rect = pygame.Rect(0, 0, size[0], size[1])
        self.ui_components = UIGroup()
        self.surface = pygame.Surface(self.size, pygame.SRCALPHA)
        self.state = Window.STATE_INVALID

    def draw(self):
        self.surface.fill((0, 0, 0, 255))
        self.ui_components.draw(self.surface)

    @property
    def image(self):
        if self.state == Window.STATE_INVALID:
            self.draw()
            self.state = Window.STATE_VALID
        return self.surface

    def on_tick(self):
        self.ui_components.on_tick()
        self.state = Window.STATE_INVALID

    def on_event(self, event):
        self.ui_components.update(event)
        self.state = Window.STATE_INVALID
