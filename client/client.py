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
from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QVBoxLayout, QDialog, QCheckBox, QPushButton, QToolTip, \
    QDesktopWidget, QApplication, QLabel, QLineEdit, QMdiSubWindow, QMdiArea, QScrollArea, QAbstractButton, QMessageBox
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class PicButton(QAbstractButton):
    def __init__(self, pixmap, pixmap_hover, pixmap_pressed, pixmap_hover_pressed, parent=None):
        super(PicButton, self).__init__(parent)
        self.pixmap = pixmap
        self.pixmap_hover = pixmap_hover
        self.pixmap_pressed = pixmap_pressed
        self.pixmap_hover_pressed = pixmap_hover_pressed
        self.setCheckable(True)
        self.setChecked(False)
        self.pressed.connect(self.update)
        self.released.connect(self.update)

    def paintEvent(self, event):
        if self.isChecked():
            if self.underMouse():
                pix = self.pixmap_hover_pressed
            else:
                pix = self.pixmap_pressed
        else:
            if self.underMouse():
                pix = self.pixmap_hover
            else:
                pix = self.pixmap


        painter = QPainter(self)
        painter.drawPixmap(event.rect(), pix)

    def enterEvent(self, event):
        self.update()

    def leaveEvent(self, event):
        self.update()

    def sizeHint(self):
        return QSize(200, 200)

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
        self.heading = QLabel("PyBot", self)
        self.heading.setStyleSheet("QLabel {font-size: 80px; color:white}")
        self.heading.move(heading_h, heading_w)
        self.heading.adjustSize()

        self.login = QLabel("User: ", self)
        self.login.setStyleSheet("QLabel {font-size: 40px; color: white}")
        login_w, login_h = WINDOW_SIZE[1] * 0.28, WINDOW_SIZE[0] * 0.15
        self.login.move(login_h, login_w)
        self.login.adjustSize()

        self.user = QLineEdit(self)
        self.user.setMaxLength(15)
        self.user.setStyleSheet(
            "QLineEdit {background: white; font-size: 38px; color: black} QLineEdit:focus {background: lightgrey;}"
            "QLineEdit:placeholder {color: white;}")
        user_w, user_h = WINDOW_SIZE[1] * 0.28, WINDOW_SIZE[0] * 0.32
        self.user.setPlaceholderText("Username")
        self.user.move(user_h, user_w)
        self.user.adjustSize()

        self.psw = QLabel("Password: ", self)
        self.psw.setStyleSheet("QLabel {font-size: 40px; color: white}")
        psw_w, psw_h = WINDOW_SIZE[1] * 0.34, WINDOW_SIZE[0] * 0.15
        self.psw.move(psw_h, psw_w)
        self.psw.adjustSize()

        self.password = QLineEdit(self)
        self.password.setMaxLength(15)
        self.password.setStyleSheet(
            "QLineEdit {background: white; font-size: 38px; color: black} QLineEdit:focus {background: lightgrey;}"
            "QLineEdit:placeholder {color: white}")
        password_w, password_h = WINDOW_SIZE[1] * 0.34, WINDOW_SIZE[0] * 0.32
        self.password.move(password_h, password_w)
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText("Password")
        self.password.adjustSize()

        self.server = QLabel("Server: ", self)
        self.server.setStyleSheet("QLabel {font-size: 40px; color: white;}")
        server_w, server_h = WINDOW_SIZE[1] * 0.45, WINDOW_SIZE[0] * 0.15
        self.server.move(server_h, server_w)
        self.server.adjustSize()

        self.host = QLineEdit(self)
        self.host.setMaxLength(15)
        self.host.setStyleSheet(
            "QLineEdit {background: white; font-size: 38px; color: black} QLineEdit:focus {background: lightgrey;} "
            "QLineEdit:placeholder {color: white;}")
        host_w, host_h = WINDOW_SIZE[1] * 0.45, WINDOW_SIZE[0] * 0.32
        self.host.move(host_h, host_w)
        self.host.setPlaceholderText("Server address")
        self.host.adjustSize()

        self.connect = QPushButton('Connect', self)
        self.connect.setStyleSheet("QPushButton {font-size: 38px; background:white; color:black; width: 630px;} "
                              "QPushButton:hover {background:black; color:white; width:200px; font-size:38px;}")
        connect_w, connect_h = WINDOW_SIZE[1] * 0.6, WINDOW_SIZE[0] * 0.15
        self.connect.move(connect_h, connect_w)
        self.connect.clicked.connect(self.connect_to_server)
        self.connect.adjustSize()

        self.error_label = QLabel('', self)
        self.error_label.setStyleSheet("QLabel {font-size: 38px; color: darkred;}")
        error_w, error_h = WINDOW_SIZE[1] * 0.7, WINDOW_SIZE[0] * 0.15
        self.error_label.move(error_h, error_w)
        self.error_label.adjustSize()

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
        self.statusBar().showMessage("Connecting...")
        self.error_label.setText("ERROR: Can't connect to server")
        self.error_label.adjustSize()


class Hub(QMainWindow):
    def __init__(self):
        super().__init__()
        self.players = ["Erich Hasl", "Nils Hebach", "Malte Schneider", "Moritz Heller"]
        self.user_stats = ["10P", "1000P", "10P", "10P"]
        self.status = ["self", "online", "ingame", "ingame"]
        self.starting_height, self.starting_width = 175, 500
        self.difference = 100
        self.line_starting_height = 250
        self.chatBar = "passive"

        self.initUI()

    def initUI(self):
        self.mdi = QMdiArea
        self.statusBar()
        self.statusBar().setStyleSheet("color:white")

        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(QPixmap("resources/background.png")))
        self.setPalette(palette)

        heading_w, heading_h = WINDOW_SIZE[1] * 0.03, WINDOW_SIZE[0] * 0.03
        heading = QLabel("Hub", self)
        heading.setStyleSheet("QLabel {font-size: 80px; color:white}")
        heading.move(heading_h, heading_w)
        heading.adjustSize()

        self.button = PicButton(QPixmap("resources/play.png"), QPixmap("resources/pause.png"),
                                QPixmap("resources/wall.png"), QPixmap("resources/muted.png"), self)
        self.button.move(WINDOW_SIZE[1] * 0.05, 250)
        self.button.setToolTip("Start a new game")
        self.button.setFixedSize(QSize(150, 150))

        self.button = PicButton(QPixmap("resources/play.png"), QPixmap("resources/pause.png"),
                                QPixmap("resources/wall.png"), QPixmap("resources/muted.png"), self)
        self.button.move(WINDOW_SIZE[1] * 0.05, 500)
        self.button.setToolTip("Chat with an online user")
        self.button.setFixedSize(QSize(150, 150))

        self.button = PicButton(QPixmap("resources/play.png"), QPixmap("resources/pause.png"),
                                QPixmap("resources/wall.png"), QPixmap("resources/muted.png"), self)
        self.button.move(WINDOW_SIZE[1] * 0.05, 750)
        self.button.setFixedSize(QSize(150, 150))

        self.button = PicButton(QPixmap("resources/play.png"), QPixmap("resources/pause.png"),
                                QPixmap("resources/wall.png"), QPixmap("resources/muted.png"), self)
        self.button.move(WINDOW_SIZE[0] * 0.7, 20)
        self.button.setToolTip("Message Admin")
        self.button.setFixedSize(QSize(100, 100))

        self.button = PicButton(QPixmap("resources/play.png"), QPixmap("resources/pause.png"),
                                QPixmap("resources/wall.png"), QPixmap("resources/muted.png"), self)
        self.button.move(WINDOW_SIZE[0] * 0.8, 20)
        self.button.setToolTip("??")
        self.button.setFixedSize(QSize(100, 100))

        self.button = PicButton(QPixmap("resources/play.png"), QPixmap("resources/pause.png"),
                                QPixmap("resources/wall.png"), QPixmap("resources/muted.png"), self)
        self.button.move(WINDOW_SIZE[0] * 0.9, 20)
        self.button.setToolTip("Join Tournament")
        self.button.setFixedSize(QSize(100, 100))

        for player in self.players:
            #TODO: Sort so that user is at the top and ingame players at the bottom
            #TODO: add player status
            label = QLabel(player, self)
            label.setStyleSheet("QLabel {font-size: 40px; color: white}")
            height, width = self.starting_height + self.difference * self.players.index(player), self.starting_width
            label.move(width, height)
            label.adjustSize()
            label2 = QLabel(self.user_stats[self.players.index(player)], self)
            label2.setStyleSheet("QLabel {font-size: 40px; color: white}")
            label2.move(1200, height)
            label2.adjustSize()

            if self.chatBar is "passive":
                pass
        setup = settings.get_standard_settings()
        header = "PyBot {}".format(setup["version"])
        self.setWindowTitle(header)
        self.setWindowIcon(QIcon(ICON_PATH))
        self.setGeometry(300, 300, *WINDOW_SIZE)
        self.center()

        self.show()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawLines(qp)
        qp.end()

    def drawLines(self, qp):
        pen = QPen(Qt.white, 5, Qt.SolidLine)
        qp.setPen(pen)
        qp.drawLine(0, 150, WINDOW_SIZE[0], 150)
        qp.drawLine(250, 150, 250, WINDOW_SIZE[1])
        for player in self.players:
            pen = QPen(Qt.white, 2, Qt.SolidLine)
            qp.setPen(pen)
            line_height = self.line_starting_height + self.difference * self.players.index(player)
            qp.drawLine(250, line_height, WINDOW_SIZE[0], line_height)


    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def quitbtnpressed(self, button):
        if button.text() == "quit":
            app,quit()
        string = "Quitting the application"
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

    ex = Hub()

    sys.exit(app.exec_())
