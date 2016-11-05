#!/usr/bin/python
# -*- coding: iso-8859-15 -*-"

import pygame


class App():

    def __init__(self):
        pygame.init()
        self.return_code = -1

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
