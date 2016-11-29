#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

import pygame
import dialog


class App():

    def __init__(self, display):
        pygame.init()
        self.return_code = -1
        self.display = display
        dialog.init(self)

    def on_event(self, event):
        pass

    def on_tick(self):
        pass

    def on_render(self):
        pass

    def exec_(self):
        clock = pygame.time.Clock()
        self._running = True
        self.on_render()
        while(self._running):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop()
                    break
                self.on_event(event)
            self.on_tick()
            self.on_render()
            clock.tick()

        return self.return_code

    def stop(self, *args):
        self.return_code = -1
        self._running = False

    @property
    def dialog(self):
        return self.__dialog

    @dialog.setter
    def dialog(self, new):
        self.__dialog = new
        if new is None:
            return
        new.on_finish = self.reset_dialog
        rect = self.display.get_rect()
        x = rect.centerx - new.size[0] * 0.5
        y = rect.centery - new.size[1] * 0.6
        print("x y", x, y)
        self.dialog_pos = (x, y)
