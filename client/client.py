#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

import socket_client
from collections import deque
import pickle
import settings
import updates
import sys
from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QVBoxLayout, QDialog, QCheckBox, QPushButton, QToolTip, \
    QDesktopWidget, QApplication, QLabel, QLineEdit, QMdiSubWindow, QMdiArea, QScrollArea, QAbstractButton, \
    QMessageBox, QGroupBox, QFormLayout, QComboBox, QWidget
from PyQt5.QtGui import *
from PyQt5.QtCore import *


BOARD_SIZE = (1017, 1017)
WINDOW_SIZE = [1500, 1017]
ICON_PATH= "resources/pybot_logo_ver1.png"
PICTURE_DICT = {"self": "resources/self.png", "online": "resources/online.png", "ingame": "resources/ingame.png"}


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
        setting = settings.get_standard_settings()
        self.user.setText(setting["username"])
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
        self.host.setText(setting["host"])
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
        self.setFixedSize(*WINDOW_SIZE)
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def connect_to_server(self):
        setting = settings.get_standard_settings()
        if setting["updating"] == "always":
            setting["host"] = self.host.text()
            setting["username"] = self.user.text()
            settings.update_standard_settings(setting)
        elif setting["updating"] == "none":
            if self.host.text() != setting["host"] or self.user.text() != setting["username"]:
                setting["host"] = self.host.text()
                setting["username"] = self.user.text()
                self.ask_to_update = QDialog(self)
                self.ask_to_update.setWindowTitle("Update Settings?")
                self.ask_to_update.setStyleSheet("QDialog {background:plum}")
                label1 = QLabel("Update Settings?", self.ask_to_update)
                label1.setStyleSheet("QLabel {color:white; font:24px}")
                button1 = QPushButton("Ok", self.ask_to_update)
                button1.setStyleSheet("QPushButton {background:salmon} QPushButton:hover {background:skyblue}")
                button2 = QPushButton("No", self.ask_to_update)
                button2.setStyleSheet("QPushButton {background:salmon} QPushButton:hover {background:skyblue}")
                button1.move(50, 50)
                button1.setFixedSize(QSize(90, 50))
                button2.setFixedSize(QSize(90, 50))
                button2.move(150, 50)
                #TODO: add func
                label1.move(50, 10)
                self.ask_to_update.setModal(True)
                self.ask_to_update.setFixedSize(300, 125)
                self.ask_to_update.setGeometry(400, 400, 300, 125)
                self.ask_to_update.show()
            else:
                pass
        else:
            pass
        self.statusBar().showMessage("Connecting...")
        self.error_label.setText("ERROR: Can't connect to server")
        self.error_label.adjustSize()


class Hub(QMainWindow):
    def __init__(self):
        super().__init__()
        self.players = ["Erich Hasl", "Nils Hebach", "Malte Schneider", "Moritz Heller"]
        self.user_stats = ["10P", "42P", "10P", "10P"]
        self.status = ["self", "online", "online", "online"]
        self.user = self.players[self.status.index('self')]
        self.starting_height, self.starting_width = 175, 500
        self.difference = 100
        self.line_starting_height = 250
        self.chatBar = "passive"
        self.layout = QHBoxLayout()
        self.chatDictionary = {}
        self.chatListDictionary = {}

        self.initUI()

    def initUI(self):
        self.mdi = QMdiArea
        self.statusBar()
        self.statusBar().setStyleSheet("color:white")
        self.statusBar().showMessage("Initialising")

        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(QPixmap("resources/background.png")))
        self.setPalette(palette)

        heading_w, heading_h = WINDOW_SIZE[1] * 0.03, WINDOW_SIZE[0] * 0.03
        heading = QLabel("Hub", self)
        heading.setStyleSheet("QLabel {font-size: 80px; color:white}")
        heading.move(heading_h, heading_w)
        heading.adjustSize()

        self.new_game = PicButton(QPixmap("resources/play.png"), QPixmap("resources/pause.png"),
                                QPixmap("resources/wall.png"), QPixmap("resources/muted.png"), self)
        self.new_game.move(WINDOW_SIZE[1] * 0.05, 250)
        self.new_game.setToolTip("Start a new game")
        self.new_game.clicked.connect(self.game_challenge)
        self.new_game.setFixedSize(QSize(150, 150))

        self.chat_button = PicButton(QPixmap("resources/chat.png"), QPixmap("resources/chat_hover.png"),
                                QPixmap("resources/chat.png"), QPixmap("resources/chat_hover.png"), self)
        self.chat_button.move(WINDOW_SIZE[1] * 0.05, 500)
        self.chat_button.setToolTip("Chat with an online user")
        self.chat_button.clicked.connect(self.choose_chat_user)
        self.chat_button.setFixedSize(QSize(150, 150))

        self.settings = PicButton(QPixmap("resources/settings.png"), QPixmap("resources/settings_hover.png"),
                                QPixmap("resources/settings.png"), QPixmap("resources/settings_hover.png"), self)
        self.setToolTip("View Settings")
        self.settings.clicked.connect(self.show_settings)
        self.settings.move(WINDOW_SIZE[1] * 0.05, 750)
        self.settings.setFixedSize(QSize(150, 150))

        self.button = PicButton(QPixmap("resources/play.png"), QPixmap("resources/pause.png"),
                                QPixmap("resources/wall.png"), QPixmap("resources/muted.png"), self)
        self.button.move(WINDOW_SIZE[0] * 0.7, 20)
        self.button.setToolTip("Message Admin")
        self.button.setFixedSize(QSize(100, 100))

        self.button = PicButton(QPixmap("resources/play.png"), QPixmap("resources/pause.png"),
                                QPixmap("resources/wall.png"), QPixmap("resources/muted.png"), self)
        self.button.move(WINDOW_SIZE[0] * 0.8, 20)
        self.button.setToolTip("Browse AI's")
        self.button.setFixedSize(QSize(100, 100))

        self.join_tournament = PicButton(QPixmap("resources/join_tournament.png"), QPixmap("resources/join_tournament_hover.png"),
                                QPixmap("resources/join_tournament.png"), QPixmap("resources/join_tournament_hover.png"), self)
        self.join_tournament.move(WINDOW_SIZE[0] * 0.9, 20)
        self.join_tournament.setToolTip("Join Tournament")
        self.join_tournament.setFixedSize(QSize(100, 100))

        for player in self.players:
            #TODO: Sort so that user is at the top and ingame players at the bottom
            #TODO: add player status
            statusImage = QLabel(self)
            statusImage.setFixedSize(QSize(32, 32))
            statusPicture = QPixmap(PICTURE_DICT[self.status[self.players.index(player)]])
            myScaledPixmap = statusPicture.scaled(statusImage.size(), Qt.KeepAspectRatio)
            statusImage.setPixmap(myScaledPixmap)
            height, width = self.starting_height + self.difference * self.players.index(player) + 10, self.starting_width - 150
            statusImage.move(width, height)

            label = QLabel(player, self)
            label.setStyleSheet("QLabel {font-size: 40px; color: white}")
            height, width = self.starting_height + self.difference * self.players.index(player), self.starting_width
            label.move(width, height)
            label.adjustSize()
            label2 = QLabel(self.user_stats[self.players.index(player)], self)
            label2.setStyleSheet("QLabel {font-size: 40px; color: white}")
            label2.move(1200, height)
            label2.adjustSize()

        self.draw_chat("Global Chat")
        setup = settings.get_standard_settings()
        header = "PyBot {}".format(setup["version"])
        self.setWindowTitle(header)
        self.setWindowIcon(QIcon(ICON_PATH))
        self.setGeometry(300, 300, *WINDOW_SIZE)
        self.setFixedSize(*WINDOW_SIZE)
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

    def get_new_message(self):
        return None

    def update_chat(self):
        if self.chatBar == "passive":
            self.chatBar = "active"
            string = "The chat is now {}".format(self.chatBar)
            self.statusBar().showMessage(string)
            self.draw_chat(receiver="Global Chat")
        else:
            self.chatBar = "passive"
            string = "The chat is now {}".format(self.chatBar)
            self.statusBar().showMessage(string)
            self.draw_chat(receiver="Global Chat")

    def draw_chat(self, receiver):
        self.initChatDict()
        if self.chatBar is "passive":
            try:
                #deleting previous items
                self.chat.deleteLater()
                self.message.deleteLater()
                self.send.deleteLater()
                self.heading.deleteLater()
                self.scroll.deleteLater()
            except:
                pass
            if self.get_new_message() is None:
                self.chat = PicButton(QPixmap("resources/chat_old_collapsed.png"), QPixmap("resources/chat_old_collapsed.png"),
                                 QPixmap("resources/chat_old_collapsed.png"), QPixmap("resources/chat_old_collapsed.png"),
                                 self)
                self.chat.setFixedSize(QSize(798, 75))
                self.setToolTip("")
                self.chat.clicked.connect(self.update_chat)
                self.chat.move(WINDOW_SIZE[0]-798, WINDOW_SIZE[1]-75)
                self.chat.raise_()
                self.chat.show()
            else:
                self.chat = PicButton(QPixmap("resources/chat_new_collapsed.png"),
                                 QPixmap("resources/chat_new_collapsed.png"),
                                 QPixmap("resources/chat_new_collapsed.png"),
                                 QPixmap("resources/chat_new_collapsed.png"),
                                 self)
                self.chat.setFixedSize(QSize(798, 75))
                self.chat.clicked.connect(self.update_chat)
                self.chat.move(WINDOW_SIZE[0] - 798, WINDOW_SIZE[1] - 75)
                self.chat.raise_()
                self.chat.show()
        else:
            try:
                #deleting previous items
                self.chat.deleteLater()
                self.message.deleteLater()
                self.send.deleteLater()
                self.heading.deleteLater()
                self.scroll.deleteLater()
            except:
                pass
            if self.get_new_message() is None:
                self.chat = PicButton(QPixmap("resources/chat_no_new.png"), QPixmap("resources/chat_no_new.png"),
                                 QPixmap("resources/chat_no_new.png"), QPixmap("resources/chat_no_new.png"),
                                 self)
                self.chat.setFixedSize(QSize(798, 547))
                self.chat.clicked.connect(self.update_chat)
                self.chat.move(WINDOW_SIZE[0] - 798, WINDOW_SIZE[1] - 547)
                self.chat.raise_()

                self.heading = QLabel(receiver, self)
                self.heading.move(WINDOW_SIZE[0] - 550, WINDOW_SIZE[1] - 475)
                self.heading.setStyleSheet("QLabel {color:black; font-size:40px}")
                self.heading.adjustSize()

                self.message = QLineEdit(self)
                self.message.setMaxLength(26)
                self.message.setStyleSheet(
                    "QLineEdit {background: white; font-size: 30px; color: black} QLineEdit:focus {background: lightgrey;} "
                    "QLineEdit:placeholder {color: white;}")
                host_w, host_h = WINDOW_SIZE[0] - 700, WINDOW_SIZE[1] - 100
                self.message.move(host_w, host_h)
                self.message.setPlaceholderText("Message")
                self.message.setFixedSize(QSize(500, 40))
                self.message.raise_()

                self.send = PicButton(QPixmap("resources/play.png"), QPixmap("resources/play.png"),
                                      QPixmap("resources/play.png"), QPixmap("resources/play.png"), self)
                self.send.setFixedSize(40, 40)
                send_w, send_h = WINDOW_SIZE[0] - 150, WINDOW_SIZE[1] - 100
                self.send.move(send_w, send_h)
                self.send.clicked.connect(lambda ignore, receiver_ = str(receiver), message = str(self.message.text()):
                                          self.send_message(receiver_, message))

                self.scroll = QScrollArea(self)
                self.scroll.setStyleSheet("QScrollArea {background:white; border:none}")
                self.scroll.move(WINDOW_SIZE[0]- 700, WINDOW_SIZE[1]- 400)
                self.scroll.setFixedSize(590, 250)
                self.scroll.raise_()
                scrollContent = QWidget(self.scroll)
                scrollContent.setStyleSheet("QWidget {background:white}")
                scrollLayout = QVBoxLayout(scrollContent)
                scrollContent.setLayout(scrollLayout)
                for message in self.chatDictionary[receiver]:
                    sender, real_message = message.split('&')
                    if sender != self.user:
                        real_message = "".join([sender, ": ", real_message])
                        messageLabel = QLabel(real_message)
                        messageLabel.setFixedSize(570, 50)
                        messageLabel.setStyleSheet("QLabel {background:white;font-size:24px;text-align:left;}")
                    else:
                        real_message = "".join([self.user, ": ", real_message])
                        messageLabel = QLabel(real_message)
                        messageLabel.setFixedSize(570, 50)
                        messageLabel.setStyleSheet("QLabel {background:white;font-size:24px;text-align:right;}")
                    scrollLayout.addWidget(messageLabel)
                self.scroll.setWidget(scrollContent)
                self.scroll.setWidgetResizable(False)

                self.chat.show()
                self.message.show()
                self.send.show()
                self.heading.show()
                self.show()
                self.scroll.show()

            else:
                self.chat = PicButton(QPixmap("resources/chat_new.png"),QPixmap("resources/chat_new.png"),
                                 QPixmap("resources/chat_new.png"),QPixmap("resources/chat_new.png"), self)
                self.chat.setFixedSize(QSize(798, 547))
                self.chat.clicked.connect(self.update_chat)
                self.chat.move(WINDOW_SIZE[0] - 798, WINDOW_SIZE[1] - 547)
                self.chat.raise_()

                self.heading = QLabel(receiver, self)
                self.heading.move(WINDOW_SIZE[0] - 700, WINDOW_SIZE[1] - 500)
                self.heading.setStyleSheet("QLabel {color:black; font-size:18px}")
                self.heading.adjustSize()

                self.message = QLineEdit(self)
                self.message.setMaxLength(30)
                self.message.setStyleSheet(
                    "QLineEdit {background: white; font-size: 30px; color: black} "
                    "QLineEdit:focus {background: lightgrey;} "
                    "QLineEdit:placeholder {color: white;}")
                host_w, host_h = WINDOW_SIZE[0] - 700, WINDOW_SIZE[1] - 100
                self.message.move(host_w, host_h)
                self.message.setPlaceholderText("Message")
                self.message.setFixedSize(QSize(500, 40))
                self.message.raise_()

                self.message = PicButton(QPixmap("resources/play.png"), QPixmap("resources/play.png"),
                                      QPixmap("resources/play.png"),QPixmap("resources/play.png"), self)
                self.send.setFixedSize(40, 40)
                self.send.clicked.connect(self.send_message)
                send_w, send_h = WINDOW_SIZE[0] - 700, WINDOW_SIZE[1] - 100
                self.send.move(send_w, send_h)
                self.chat.show()
                self.message.show()
                self.send.show()
                self.heading.show()
                self.show()

    def choose_chat_user(self):
        chatable_user = ['Global Chat']
        for i in range(0, len(self.status)):
            if self.status[i] == "online":
                chatable_user.append(self.players[i])
        self.chat_choose_window = QDialog(self)
        chat_choose_width = 300
        chat_choose_height = 300
        print(chatable_user)
        self.chat_choose_window.setGeometry(300, 300, chat_choose_height, chat_choose_width)
        self.chat_choose_window.setWindowTitle("Choose a User")
        user_button_list = []
        for i in range(0, len(chatable_user)):
            print(chatable_user[i])
            user_button = QPushButton(str(chatable_user[i]), self.chat_choose_window)
            user_button.setStyleSheet("QPushButton {background:salmon;color:black;} "
                                           "QPushButton:hover {background:skyblue; color:black;}")
            width, height = chat_choose_width, chat_choose_height/len(chatable_user)
            user_button.setFixedSize(QSize(width, height))
            user_button.move(0, height*i)
            usertext = str(user_button.text())
            user_button_list.append(user_button)
            user_button.clicked.connect(lambda ignore, text_=str(usertext): self.start_chat(text_))
        for button in user_button_list:
            button.show()
        self.chat_choose_window.setFixedSize(chat_choose_height, chat_choose_width)
        self.chat_choose_window.show()

    def game_challenge(self):
        playable_user = []
        for i in range(0, len(self.status)):
            if self.status[i] == "online":
                playable_user.append(self.players[i])
        self.challenge = QDialog(self)
        chat_choose_width = 300
        chat_choose_height = 300
        self.challenge.setGeometry(300, 300, chat_choose_height, chat_choose_width)
        self.challenge.setWindowTitle("Choose an Opponent")
        for i in range(0, len(playable_user)):
            user_button = QPushButton(str(playable_user[i]), self.challenge)
            user_button.setStyleSheet("QPushButton {background:salmon;color:black;} "
                                           "QPushButton:hover {background:skyblue; color:black;}")
            width, height = chat_choose_width, chat_choose_height/len(playable_user)
            user_button.setFixedSize(QSize(width, height))
            user_button.move(0, height*i)
            usertext = str(user_button.text())
            user_button.clicked.connect(lambda usertext=usertext: self.start_game(usertext))
        self.challenge.setFixedSize(chat_choose_height, chat_choose_width)
        self.challenge.show()

    def start_game(self, user):
        self.challenge.close()
        self.statusBar().showMessage("Starting game against {}".format(user))

    def start_chat(self, username_):
        self.chat_choose_window.close()
        self.chatBar = "active"
        self.draw_chat(receiver=username_)

    def show_settings(self):
        self.statusBar().showMessage("Opening settings...")
        self.new_window = QDialog(self)
        setting = settings.get_standard_settings()
        username_label = QLabel("Username: ", self.new_window)
        username_label.setStyleSheet("QLabel {font-size: 15px; color: black}")
        username_label.move(15, 14)
        self.user = QLineEdit(self.new_window)
        self.user.setMaxLength(15)
        self.user.setStyleSheet(
            "QLineEdit {background: white; font-size: 15px; color: black} QLineEdit:focus {background: lightgrey;}"
            "QLineEdit:placeholder {color: white;}")
        old_username = setting["username"]
        self.user.setPlaceholderText(old_username)
        self.user.move(120, 10)
        self.user.adjustSize()
        hostname = QLabel("Host: ", self.new_window)
        hostname.setStyleSheet("QLabel {font-size: 15px; color: black}")
        hostname.move(15, 54)
        self.host = QLineEdit(self.new_window)
        self.host.setMaxLength(15)
        self.host.setStyleSheet(
            "QLineEdit {background: white; font-size: 15px; color: black} QLineEdit:focus {background: lightgrey;}"
            "QLineEdit:placeholder {color: white;}")
        old_hostname = setting["host"]
        self.host.setPlaceholderText(old_hostname)
        self.host.move(120, 50)
        self.host.adjustSize()
        update_behaviour = QLabel("Update settings:", self.new_window)
        update_behaviour.setStyleSheet("QLabel {font-size: 15px; color: black}")
        update_behaviour.move(75, 125)
        self.always_update = QPushButton("Always", self.new_window)
        self.always_update.setStyleSheet("QPushButton {background: white} QPushButton:hover {background:lightblue}"
                                    "QPushButton:checked {background:black; color:white}")
        self.always_update.setCheckable(True)
        if setting["updating"]=="always":
            self.always_update.setChecked(True)
        self.always_update.move(50, 150)
        self.always_update.clicked.connect(self.disable_never)
        self.never_update = QPushButton("Never", self.new_window)
        self.never_update.setCheckable(True)
        if setting["updating"] == "never":
            self.never_update.setChecked(True)
        self.never_update.setStyleSheet("QPushButton {background: white} QPushButton:hover {background:lightblue}"
                                   "QPushButton:checked {color:white; background:black}")
        self.never_update.move(175, 150)
        self.never_update.clicked.connect(self.disable_always)
        version_string = "Version {}".format(setting["version"])
        version = QLabel(version_string, self.new_window)
        version.setStyleSheet("QLabel {font-size: 12px; color: black}")
        version.move(15, 280)
        self.ok = QPushButton("Ok", self.new_window)
        self.ok.setStyleSheet("QPushButton {background: white} QPushButton:hover {background:lightblue}")
        self.ok.clicked.connect(self.update_settings)
        self.ok.move(15, 225)
        self.cancel = QPushButton("Cancel", self.new_window)
        self.cancel.setStyleSheet("QPushButton {background: white} QPushButton:hover {background:red; color:white}")
        self.cancel.clicked.connect(self.cancle)
        self.cancel.move(150, 225)
        self.new_window.setModal(True)
        self.new_window.move(500, 500)
        self.new_window.setWindowTitle("Settings")
        self.new_window.setGeometry(500, 500, 300, 300)
        self.new_window.setFixedSize(300, 300)
        self.new_window.show()

    def send_message(self, receiver, message):
        self.statusBar().showMessage("Sending message...")
        messageList = self.chatDictionary[receiver]
        message = "{}&{}".format(self.user, message)
        messageList.append(message)
        self.chatDictionary[receiver] = messageList

    def clearStatusBar(self):
        print("clearing...")
        self.statusBar().showMessage("")

    def disable_always(self):
        self.always_update.setChecked(False)

    def disable_never(self):
        self.never_update.setChecked(False)

    def update_settings(self):
        setting = settings.get_standard_settings()
        if self.host.text() != "":
            setting["host"] = self.host.text()
        if self.user.text() != "":
            setting["username"] = self.user.text()
        if self.always_update.isChecked():
            setting["updating"] = "always"
        if self.never_update.isChecked():
            setting["updating"] = "never"
        settings.update_standard_settings(setting)
        self.new_window.close()

    def cancle(self):
        self.new_window.close()

    def initChatDict(self):
        for player in self.players:
            if not player == self.user:
                try:
                    self.chatDictionary[player]
                except:
                    listkey = ''.join([player, "_list"])
                    self.chatListDictionary.update({listkey : []})
                    self.chatDictionary.update({player : self.chatListDictionary[listkey]})
                    self.send_message(player, "Hello There")
        try:
            self.chatDictionary["Global Chat"]
        except:
            listkey = ''.join(["Global Chat", "_list"])
            self.chatListDictionary.update({listkey: []})
            self.chatDictionary.update({"Global Chat": self.chatListDictionary[listkey]})


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
