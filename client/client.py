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
        if self.window.exec_() == QDialog.Accepted:
            self.window = gui.Hub(self.client)

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

    def __init__(self, *args, **kwargs):
        super(GameClient, self).__init__(*args, **kwargs)
        self.is_playing = False
        self.inits, self.updates = deque(), deque()
        self.players_invalid = False

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
        self.players_invalid = True

    def send_ai(self, path):
        with open(path, 'r') as f:
            content = f.read()
        self.send("ai {}".format(content))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Game()
    sys.exit(app.exec_())
