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
from PyQt5.QtWidgets import QDesktopWidget, QApplication, QMainWindow, QLabel, QLineEdit, QPushButton
from PyQt5.QtGui import *


class Window(QMainWindow):
    """heading_w, heading_h = self.rect.width * 0.3, self.rect.height * 0.1
    heading_rect = pygame.Rect(self.rect.width * 0.1,
                               self.rect.height * 0.1,
                               heading_w, heading_h)
    self.heading = Label("PyBot", heading_rect, (255, 255, 255, 255), 90)
    self.ui_components.add(self.heading)
    login_rect = pygame.Rect(self.rect.width * 0.125,
                             heading_rect.bottom + self.rect.height * 0.01,
                             self.rect.width * 0.5,
                             self.rect.height * 0.04)
    hintcolor = (100, 100, 100, 255)
    self.login_widget = TextInputWidget(login_rect, "Username      :",
                                        (255, 255, 255, 255),
                                        (40, 40, 40, 255),
                                        30, hint="Enter username",
                                        hintcolor=hintcolor)
    self.login_widget.text = setup["username"]
    self.ui_components.add(self.login_widget)

    server_rect = login_rect.copy()
    server_rect.top = login_rect.bottom + self.rect.height * 0.01
    self.server_widget = TextInputWidget(server_rect, "Server address:",
                                         (255, 255, 255, 255),
                                         (40, 40, 40, 255),
                                         30, hint="Enter server address",
                                         hintcolor=hintcolor)
    self.server_widget.text = setup["host"]
    self.ui_components.add(self.server_widget)

    conn_rect = pygame.Rect(self.rect.width * 0.125,
                            server_rect.bottom + self.rect.height * 0.02,
                            self.rect.width * 0.45,
                            self.rect.height * 0.04)
    self.btn_conn = Button("Connect", conn_rect, 30)
    self.btn_conn.clicked = self.connect
    self.ui_components.add(self.btn_conn)

    error_rect = pygame.Rect(self.rect.width * 0.125,
                             conn_rect.bottom + self.rect.height * 0.02,
                             self.rect.width * 0.5,
                             self.rect.height * 0.4)
    self.error_label = Label("", error_rect, (255, 0, 0, 255), 30)
    self.ui_components.add(self.error_label)

    info_rect = pygame.Rect(self.rect.width * 0.125,
                            conn_rect.bottom + self.rect.height * 0.1,
                            self.rect.width * 0.9,
                            self.rect.height * 0.4)
    self.info_label = Label("", info_rect, (255, 255, 255, 255), 30)
    self.ui_components.add(self.info_label)

    info_btn_rect = pygame.Rect(self.rect.width * 0.625,
                                self.rect.height * 0.05,
                                self.rect.width * 0.25,
                                self.rect.width * 0.25)

    # TODO: sqaure the images
    self.ic_no_info = pygame.image.load("resources/question.png")
    self.ic_info = pygame.image.load("resources/understood.png")
    self.info_btn = ImageButton(self.ic_no_info, info_btn_rect)
    self.info_btn.clicked = self.show_info"""

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
        print(login_w, login_h)
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

    ex = Window()

    sys.exit(app.exec_())
