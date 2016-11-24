#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

import pickle
import sys
from collections import deque
import atexit

import settings
import socket_client
import gui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QVBoxLayout, QDialog, QPushButton, QDesktopWidget, QApplication, QLabel, QLineEdit, \
    QMdiArea, QScrollArea, QAbstractButton, \
    QWidget



class Game():

    def __init__(self):
        super().__init__()
        self.client = GameClient()
        self.client.on_move = self.update_window
        self.window = gui.ServerSelect(self.client)

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

    def on_receive(self, query):
        args = query.split(b' ')
        key, body = args[0].decode("utf-8"), b" ".join(args[1:])
        print(key)
        if key == 'username':
            self.send(self.username)
            print(self.username)
        elif key == 'password':
            self.send(self.password)
        elif key == 'started':
            if not self.is_playing:
                self.started_game()
            self.is_playing = True
            self.playing_changed(self.is_playing)
        elif key == "players":
            self.players = [x.decode("utf-8") for x in body.split(b" ")]
            print(self.players)
            self.on_players(self.players)
        elif key == "init":
            initial = pickle.loads(body)
            self.on_init(initial)
        elif key == "update":
            update = pickle.loads(body)
            self.on_update(update)
        elif key == "invalid":
            self.login = "Invalid Username or Password"
        elif key == "connected":
            self.on_login()
        elif key == "chat":
            self.new_message(body.decode("utf-8"))

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
        self.players_invalid = True

    def send_ai(self, path):
        with open(path, 'r') as f:
            content = f.read()
        self.send("ai {}".format(content))

    def on_login(self):
        pass

    def on_players(self, playerlist):
        pass

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
    ex = Game()
    sys.exit(app.exec_())
