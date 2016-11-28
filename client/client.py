#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

import pickle
import sys
from collections import deque
import atexit
import socket

import settings
import socket_client
import gui
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication



class Game():

    def __init__(self):
        super().__init__()
        self.client = GameClient()
        self.client.on_move = self.update_window
        self.window = gui.ChooseScreenResolution(SCREEN_SIZE, self.client)

    def update_window(self, server):
        if server == 0:
            self.window = gui.Hub(self.client)
        elif server >= 0:
            pass

    def lobby_view(self):
        self.window = gui.Hub(self.client)

    def stop(self, *args):
        print("stopped")
        self.client.disconnect()

class GameClient(socket_client.SocketClient):

    data_received = pyqtSignal(bytes)

    def __init__(self, *args, **kwargs):
        super(GameClient, self).__init__(*args, **kwargs)
        self.data_received.connect(self.on_receive)
        self.is_playing = False
        self.inits, self.updates = deque(), deque()
        self.players = None
        self.players_invalid = False
        self.login = False

    class GameClient(socket_client.SocketClient):

        def __init__(self, *args, **kwargs):
            super(GameClient, self).__init__(*args, **kwargs)
            self.is_playing = False
            self.inits, self.updates = deque(), deque()
            self.players_invalid = False

        def on_receive(self, query):
            print("receiving", query)
            key = query["key"]
            action = query["action"]
            if key == "login":
                if action == "username":
                    self.send(self.username)
                elif action == 'password':
                    self.send(self.password)
                elif action == 'invalid':
                    self.on_login_failed()
                elif action == 'connected':
                    print("connected")
                    self.on_connect()
            elif key == "server":
                if action == "players":
                    self.players = query["players"]
                    self.players_changed()
                elif action == "moved":
                    self.on_move(query["to"], query["state"])
                elif action == "active":
                    self.on_games_info(query["servers"])
            elif key == "game":
                if action == "started":
                    if not self.is_playing:
                        self.started_game()
                    self.is_playing = True
                    self.playing_changed(self.is_playing)
                elif action == "finished":
                    self.is_playing = False

                if action == "init":
                    self.on_init(query["data"])
                elif action == "update":
                    self.on_update(query["data"])

            elif key == "chat":
                self.on_recv_chat(query["mode"], query["text"], query["from"])
            elif key == "queue":
                if action == "joined":
                    self.on_join_queue()
                elif action == "left":
                    self.on_leave_queue()

        def on_init(self, init):
            self.inits.append(init)

        def on_update(self, update):
            self.updates.append(update)

        def on_move(self, server, state):  # user was moved to server
            pass

        def on_login_failed(self):
            pass

        def on_connect(self):
            print("Default on connect")

        def on_disconnect(self):
            pass

        def on_recv_chat(self, mode, text, from_user):
            print("default onrecvchat")

        def on_join_queue(self):
            pass

        def on_leave_queue(self):
            pass

        def on_games_info(self, games):
            pass

        def chat(self, text, to="global"):
            self.send("chat {} {}".format(to, text))

        def start_game(self):
            print("starting game")
            self.send("start")

        def started_game(self):
            pass

        def playing_changed(self, new):
            pass

        def players_changed(self):
            self.players_invalid = True

        def send_ai(self, path):
            with open(path, 'r') as f:
                content = f.read()
            self.send("ai {}".format(content))

        def new_message(self, message):
            type, body = message.split(" ", 1)
            if type == "global":
                sender, message = body.split(" ", 1)
                self.on_global_chat(sender, message)
            else:
                sender, message = body.split(" ", 1)
                self.on_private_chat(sender, message)

        def on_global_chat(self, sender, body):
            pass

        def on_private_chat(self, sender, message):
            pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    desktop = app.desktop().screenGeometry()
    global SCREEN_SIZE
    SCREEN_SIZE = desktop.width(), desktop.height()
    ex = Game()
    sys.exit(app.exec_())
