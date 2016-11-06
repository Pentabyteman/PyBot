#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

import socket_client
from collections import deque
import pygame
import app
import gui
import pickle
import settings

global USER, HOST, Version
EDIT, USER, HOST, Version = settings.get_standard_settings()
BOARD_SIZE = (1017, 1017)
WINDOW_SIZE = (1500, 1017)
ICON_PATH = "resources/animation_red/robot_red_normal.png"
START_STRING = "Running PyBot {0} on {1}. with Python {2} \n ".format(Version, settings.get_pybot_platform(),
                                                               settings.get_python_version())


class Game(app.App):

    def __init__(self, display):
        super(Game, self).__init__()
        self.display = display
        self.client = GameClient()
        self.window = gui.ServerSelect(WINDOW_SIZE, self.client,
                                       host=HOST, username=USER)
        self.window.has_connected = self.start_preparation

    def start_preparation(self):
        self.window = gui.GamePreparation(WINDOW_SIZE, self.client,
                                          has_started=self.start_game)

    def start_game(self):
        self.window = gui.GameWindow(WINDOW_SIZE, BOARD_SIZE,
                                     client=self.client,
                                     on_finish=self.stop)

    def stop(self, *args):
        super(Game, self).stop(*args)
        self.client.disconnect()

    def on_event(self, event):
        self.window.on_event(event)

    def on_tick(self):
        self.window.on_tick()

    def on_render(self):
        self.display.fill((255, 255, 255))
        self.display.blit(self.window.image, (0, 0))
        pygame.display.flip()


class GameClient(socket_client.SocketClient):

    def __init__(self, *args, **kwargs):
        super(GameClient, self).__init__(*args, **kwargs)
        self.is_playing = False
        self.inits, self.updates = deque(), deque()

    def on_receive(self, query):
        args = query.split(b' ')
        key, body = args[0].decode("utf-8"), b" ".join(args[1:])
        if key == 'username':
            self.send(self.username)
        elif key == 'started':
            if not self.is_playing:
                self.started_game()
            self.is_playing = True
            self.playing_changed(self.is_playing)
        elif key == "players":
            self.players = [x.decode("utf-8") for x in body.split(b" ")]
            self.players_changed()
        elif key == "init":
            initial = pickle.loads(body)
            self.on_init(initial)
        elif key == "update":
            update = pickle.loads(body)
            self.on_update(update)

    def on_init(self, init):
        self.inits.append(init)

    def on_update(self, update):
        self.updates.append(update)

    def start_game(self):
        print("starting game")
        self.send("start")

    def started_game(self):
        pass

    def playing_changed(self, new):
        pass

    def players_changed(self):
        pass

    def send_ai(self, path):
        with open(path, 'r') as f:
            content = f.read()
        self.send("ai {}".format(content))


if __name__ == '__main__':
    display = pygame.display.set_mode(WINDOW_SIZE)
    print(START_STRING)
    # decorating the python window
    header = "PyBot {}".format(Version)
    pygame.display.set_caption(header)
    icon = pygame.transform.scale(pygame.image.load(ICON_PATH), (32, 32))
    pygame.display.set_icon(icon)

    game = Game(display)
    game.exec_()
