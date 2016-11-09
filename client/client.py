#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

import socket_client
from collections import deque
import pickle
import settings
import updates



BOARD_SIZE = (1017, 1017)
WINDOW_SIZE = [1500, 1017]
global ICON_PATH
ICON_PATH= "resources/pybot_logo_ver1.png"

import sys
from PyQt5.QtWidgets import QDesktopWidget, QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QAction
from PyQt5.QtGui import *
from PyQt5.QtCore import *



class ServerSelect(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, *WINDOW_SIZE)
        self.center()

        self.statusBar()
        self.statusBar().setStyleSheet("color:white")

        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(QPixmap("resources/background.png")))
        self.setPalette(palette)

        heading_w, heading_h = WINDOW_SIZE[1] * 0.1, WINDOW_SIZE[0] * 0.1
        heading = QLabel("PyBot", self)
        heading.setStyleSheet("QLabel {font-size: 80px; color:white}")
        heading.move(heading_h, heading_w)
        heading.adjustSize()

        login = QLabel("User: ", self)
        login.setStyleSheet("QLabel {font-size: 40px; color: white}")
        login_w, login_h = WINDOW_SIZE[1] * 0.28, WINDOW_SIZE[0] * 0.15
        login.move(login_h, login_w)
        login.adjustSize()

        user = QLineEdit(self)
        user.setMaxLength(15)
        user.setStyleSheet(
            "QLineEdit {background: white; font-size: 38px; color: black} QLineEdit:focus {background: lightgrey;}"
            "QLineEdit:placeholder {color: white;}")
        user_w, user_h = WINDOW_SIZE[1] * 0.28, WINDOW_SIZE[0] * 0.32
        user.setPlaceholderText("Username")
        user.move(user_h, user_w)
        user.adjustSize()

        psw = QLabel("Password: ", self)
        psw.setStyleSheet("QLabel {font-size: 40px; color: white}")
        psw_w, psw_h = WINDOW_SIZE[1] * 0.34, WINDOW_SIZE[0] * 0.15
        psw.move(psw_h, psw_w)
        psw.adjustSize()

        password = QLineEdit(self)
        password.setMaxLength(15)
        password.setStyleSheet(
            "QLineEdit {background: white; font-size: 38px; color: black} QLineEdit:focus {background: lightgrey;}"
            "QLineEdit:placeholder {color: white}")
        password_w, password_h = WINDOW_SIZE[1] * 0.34, WINDOW_SIZE[0] * 0.32
        password.move(password_h, password_w)
        password.setEchoMode(QLineEdit.Password)
        password.setPlaceholderText("Password")
        password.adjustSize()

        server = QLabel("Server: ", self)
        server.setStyleSheet("QLabel {font-size: 40px; color: white;}")
        server_w, server_h = WINDOW_SIZE[1] * 0.45, WINDOW_SIZE[0] * 0.15
        server.move(server_h, server_w)
        server.adjustSize()

        host = QLineEdit(self)
        host.setMaxLength(15)
        host.setStyleSheet(
            "QLineEdit {background: white; font-size: 38px; color: black} QLineEdit:focus {background: lightgrey;} "
            "QLineEdit:placeholder {color: white;}")
        host_w, host_h = WINDOW_SIZE[1] * 0.45, WINDOW_SIZE[0] * 0.32
        host.move(host_h, host_w)
        host.setPlaceholderText("Server address")
        host.adjustSize()

        connect = QPushButton('Connect', self)
        connect.setStyleSheet("QPushButton {font-size: 38px; background:white; color:black; width: 630px;} "
                              "QPushButton:hover {background:black; color:white; width:200px; font-size:38px;}")
        connect_w, connect_h = WINDOW_SIZE[1] * 0.6, WINDOW_SIZE[0] * 0.15
        connect.move(connect_h, connect_w)
        connect.clicked.connect(self.connect_to_server)
        connect.adjustSize()

        setup = settings.get_standard_settings()
        header = "PyBot {}".format(setup["version"])
        self.setWindowTitle(header)
        self.setWindowIcon(QIcon(ICON_PATH))
        info = "Running PyBot {0} on {1}. with Python {2} \n " \
            .format(setup["version"], settings.get_pybot_platform(),
                    settings.get_python_version())
        print(info)
        self.statusBar().showMessage(info)
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def connect_to_server(self):
        self.statusBar().showMessage("Connecting")

class Hub(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, *WINDOW_SIZE)
        self.center()

        self.statusBar()
        self.statusBar().setStyleSheet("color:white")

        exitAction = QAction(QIcon('resources/quit.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(app.quit)

        self.button_quit = QPushButton()
        self.button_quit.setIcon(QIcon('resources/wall.png'))
        self.button_quit.setIconSize(QSize(100, 100))
        self.button_quit.adjustSize()

        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(QPixmap("resources/background.png")))
        self.setPalette(palette)

        heading_w, heading_h = WINDOW_SIZE[1] * 0.03, WINDOW_SIZE[0] * 0.03
        heading = QLabel("Hub", self)
        heading.setStyleSheet("QLabel {font-size: 80px; color:white}")
        heading.move(heading_h, heading_w)
        heading.adjustSize()

        setup = settings.get_standard_settings()
        header = "PyBot {}".format(setup["version"])
        self.setWindowTitle(header)
        self.setWindowIcon(QIcon(ICON_PATH))

        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def toolbtnpressed(self, button):
        if button.text() == "quit":
            app,quit()
        string = "Hi"
        self.statusBar().showMessage(string)

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

    ex = ServerSelect()

    sys.exit(app.exec_())
