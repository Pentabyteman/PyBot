#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

import settings
import time
import pygame
import string

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QVBoxLayout, QDialog, QPushButton, QDesktopWidget, QLabel, \
    QLineEdit, QMdiArea, QScrollArea, QAbstractButton, QWidget, QStatusBar, QGridLayout, QTextEdit, QSizePolicy, \
    QRadioButton, QButtonGroup


BOARD_SIZE = (1017, 1017)
WINDOW_SIZE = [1280, 800]
ICON_PATH = "resources/pybot_logo_ver1.png"
PICTURE_DICT = {"self": "resources/self.png", "online": "resources/online.png", "ingame": "resources/ingame.png"}
RESOLUTIONS = ["1920x1200 8:5", "1920x1080 16:9","1680x1050 8:5", "1600x900 16:9", "1440x900 8:5", "1360x768 16:9",
               "1280x1024 5:4", "1280x800 8:5", "1280x720 16:9", "1024x768 4:3"]
SCREEN_DICT = {
    "1920x1200": [1500, 1017],
    "1920x1080": [1350, 915],
    "1680x1050": [1313, 890],
    "1600x900": [1125, 763],
    "1440x900": [1125, 763],
    "1360x768": [960, 650],
    "1280x1024": [1180, 800],
    "1280x800": [1000, 678],
    "1280x720": [900, 610],
    "1024x768": [960, 650]
    }


class ChooseScreenResolution(QDialog):
    def __init__(self, Screen, client):
        super().__init__()
        self.client = client
        self.screen = Screen
        self.initUI()

    def initUI(self):
        # Calculating height and width of window
        self.width = (self.screen[1] / 2)
        self.height = (self.screen[1] / 2)
        self.setGeometry(0, 0, self.width, self.height)

        # Creating Title Label and Layouts
        self.title = QLabel('Choose A Screen Resolution', self)
        self.title.setStyleSheet('QLabel {color:white; font-size:40px}')
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.title)
        self.group = QButtonGroup()
        self.layout.addStretch()

        # Creating Radiobuttons for Screen Resolutions
        for resolution in RESOLUTIONS:
            button = QRadioButton(resolution, self)
            button.setStyleSheet('QRadioButton {color:white} QRadioButton:hover {color:black; font-weight:bold;}')
            self.layout.addWidget(button)
            self.group.addButton(button)
            self.recommended_setting(button=button, resolution=resolution)
        self.check_atleastone()

        # Creating the Enter-Button
        self.enter = QPushButton('Start', self)
        self.enter.setStyleSheet("QPushButton {font-size: 20px; background:white; color:black;} "
                                 "QPushButton:hover {background:black; color:white; font-size:20px;}")
        self.enter.clicked.connect(self.on_start)
        self.enter.setFixedSize(self.width/2, 40)
        self.layout.addWidget(self.enter)
        self.setLayout(self.layout)

        # Drawing the Background
        palette = QPalette()
        picture = QPixmap("resources/background.png")
        picture_scaled = picture.scaled(self.height, self.width)
        palette.setBrush(QPalette.Background, QBrush(picture_scaled))
        self.setPalette(palette)

        # Adding Window Title and Logo
        setup = settings.get_standard_settings()
        header = "PyBot v{}".format(setup["version"])
        self.setWindowTitle(header)
        self.setWindowIcon(QIcon(ICON_PATH))
        info = "Running PyBot {0} on {1}. with Python {2} \n " \
            .format(setup["version"], settings.get_pybot_platform(),
                    settings.get_python_version())
        print(info)
        self.setFixedSize(self.width, self.height)
        self.center()
        self.show()

    def on_start(self):
        try:
            checked_button = self.group.checkedButton()
            resolution = checked_button.text()
            key = resolution.split(' ')[0]
            optimal_size = SCREEN_DICT[key]
            self.serverselect = ServerSelect(self.client, optimal_size)
            self.serverselect.show()
            self.close()
        except:
            self.serverselect = ServerSelect(self.client)
            self.serverselect.show()
            self.close()

    def recommended_setting(self, button, resolution):
        width, other = resolution.split('x')
        height = other.split(' ')[0]
        if int(width) == self.screen[0] and int(height) == self.screen[1]:
            current_text = button.text()
            new_text = "{} (Recommended)".format(current_text)
            button.setStyleSheet('QRadioButton {font-weight:bold; color:white} QRadioButton:hover {color:black}')
            button.setChecked(True)
            button.setText(new_text)

    def check_atleastone(self):
        try:
            checked_button = self.group.checkedButton()
        except:
            self.group.buttons[0].setChecked(True)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


class ServerSelect(QDialog):
    def __init__(self, client, Window_Size=WINDOW_SIZE ):
        super().__init__()
        self.Window_Size = Window_Size
        self.client = client
        self.info_state = True
        self.established_connection = False
        self.initUI()

    def initUI(self):
        # Creating the Window
        self.setGeometry(300, 300, *self.Window_Size)
        self.center()

        # Creating the Statusbar
        self.statusbar = QStatusBar()
        self.statusbar.setStyleSheet("QLabel {color:white;}")

        # Drawing the Background
        palette = QPalette()
        picture = QPixmap("resources/background.png")
        picture_scaled = picture.scaled(self.Window_Size[1], self.Window_Size[0])
        palette.setBrush(QPalette.Background, QBrush(picture_scaled))
        self.setPalette(palette)

        # Creating the Heading
        self.heading = QLabel("PyBot", self)
        self.heading.setStyleSheet("QLabel {font-size: 80px; color:white}")

        # The User-Label
        self.login = QLabel("User: ", self)
        self.login.setStyleSheet("QLabel {font-size: 40px; color: white}")

        # The User-Input Field
        self.user = QLineEdit(self)
        setting = settings.get_standard_settings()
        self.user.setText(setting["username"])
        self.user.setMaxLength(15)
        self.user.setStyleSheet(
            "QLineEdit {background: white; font-size: 38px; color: black} QLineEdit:focus {background: lightgrey;}"
            "QLineEdit:placeholder {color: white;}")
        self.user.setPlaceholderText("Username")

        # The Password Label
        self.psw = QLabel("Password: ", self)
        self.psw.setStyleSheet("QLabel {font-size: 40px; color: white}")

        # The Password-Input Field
        self.password = QLineEdit(self)
        self.password.setMaxLength(15)
        self.password.setStyleSheet(
            "QLineEdit {background: white; font-size: 38px; color: black} QLineEdit:focus {background: lightgrey;}"
            "QLineEdit:placeholder {color: white}")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText("Password")

        # The Server Label
        self.server = QLabel("Server: ", self)
        self.server.setStyleSheet("QLabel {font-size: 40px; color: white;}")

        # The Sevrer-Input Field
        self.host = QLineEdit(self)
        self.host.setMaxLength(19)
        self.host.setStyleSheet(
            "QLineEdit {background: white; font-size: 38px; color: black} QLineEdit:focus {background: lightgrey;} "
            "QLineEdit:placeholder {color: white;}")
        self.host.setPlaceholderText("Server address")
        self.host.setText(setting["host"])

        # The Connect-Button
        self.connect = QPushButton('Connect', self)
        self.connect.setStyleSheet("QPushButton {font-size: 38px; background:white; color:black; width: 630px;} "
                                   "QPushButton:hover {background:black; color:white; width:200px; font-size:38px;}")
        self.connect.clicked.connect(lambda ignore: self.connect_to_server(self.user.text(), self.password.text(),
                                                                           self.host.text()))

        # The Error Label
        self.error_label = QLabel('', self)
        self.error_label.setStyleSheet("QLabel {font-size: 38px; color: darkred;}")

        # The Positions of all objects
        heading_y, heading_x = self.Window_Size[1] * 0.1, self.Window_Size[0] * 0.1
        login_y, login_x = self.Window_Size[1] * 0.28, self.Window_Size[0] * 0.15
        user_y, user_x = self.Window_Size[1] * 0.28, self.Window_Size[0] * 0.32
        psw_y, psw_x = self.Window_Size[1] * 0.34, self.Window_Size[0] * 0.15
        password_y, password_x = self.Window_Size[1] * 0.34, self.Window_Size[0] * 0.32
        server_y, server_x = self.Window_Size[1] * 0.45, self.Window_Size[0] * 0.15

        host_y, host_x = self.Window_Size[1] * 0.45, self.Window_Size[0] * 0.32
        connect_y, connect_x = self.Window_Size[1] * 0.6, self.Window_Size[0] * 0.15
        error_y, error_x = self.Window_Size[1] * 0.7, self.Window_Size[0] * 0.15

        if self.Window_Size[0] <= 1600:
            user_x = self.Window_Size[0] * 0.34
            psw_y = self.Window_Size[1] * 0.36
            password_y, password_x = self.Window_Size[1] * 0.36, self.Window_Size[0] * 0.34
            server_y = self.Window_Size[1] * 0.47
            host_y, host_x = self.Window_Size[1] * 0.47, self.Window_Size[0] * 0.34
            connect_y = self.Window_Size[1] * 0.62
            error_y = self.Window_Size[1] * 0.72

        if self.Window_Size[0] <= 1400:
            user_x = self.Window_Size[0] * 0.38
            psw_y = self.Window_Size[1] * 0.37
            password_y, password_x = self.Window_Size[1] * 0.37, self.Window_Size[0] * 0.38
            server_y = self.Window_Size[1] * 0.5
            host_y, host_x = self.Window_Size[1] * 0.5, self.Window_Size[0] * 0.38
            connect_y = self.Window_Size[1] * 0.66
            error_y = self.Window_Size[1] * 0.76

        # Moving all objects to the right place
        self.heading.move(heading_x, heading_y)
        self.heading.adjustSize()
        self.login.move(login_x, login_y)
        self.login.adjustSize()
        self.user.move(user_x, user_y)
        self.user.adjustSize()
        self.psw.move(psw_x, psw_y)
        self.psw.adjustSize()
        self.password.move(password_x, password_y)
        self.password.adjustSize()
        self.server.move(server_x, server_y)
        self.server.adjustSize()
        self.host.move(host_x, host_y)
        self.host.adjustSize()
        self.connect.move(connect_x, connect_y)
        self.connect.adjustSize()
        self.error_label.move(error_x, error_y)
        self.error_label.adjustSize()


        # Creating Window Title and Icon
        setup = settings.get_standard_settings()
        header = "PyBot v{}".format(setup["version"])
        self.setWindowTitle(header)
        self.setWindowIcon(QIcon(ICON_PATH))
        info = "Running PyBot {0} on {1}. with Python {2} \n " \
            .format(setup["version"], settings.get_pybot_platform(),
                    settings.get_python_version())
        print(info)
        self.statusbar.showMessage(info)
        self.setFixedSize(*self.Window_Size)
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def connect_to_server(self, username_, password_, server_):
        self.client.on_connect = self.on_connect
        self.client.on_login_failed = self.on_login_failed
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
                button1.clicked.connect(lambda ignore, username = self.user.text(), host = self.host.text():
                                        self.update_setting(username, host))
                button2.clicked.connect(self.quit)
                label1.move(50, 10)
                self.ask_to_update.setModal(True)
                self.ask_to_update.setFixedSize(300, 125)
                self.ask_to_update.setGeometry(400, 400, 300, 125)
                self.ask_to_update.show()
            else:
                pass
        else:
            pass
        username = username_
        server = server_
        password = password_
        if len(username) < 4 or any(x not in string.ascii_lowercase for x in
                                    username):
            print("Invalid username")
            self.error_label.setText("Invalid username")
            return
        try:
            parts = server.split(":")
            host = parts[0]
            assert len(host) > 0
            if len(parts) > 1:
                port = int(parts[1])
            else:
                port = 25555
        except Exception:
            print("Invalid address", server)
            self.error_label.setText("Invalid server address")
            return
        state = self.client.connect(host, port, username, password)
        if state:  # connected
            self.error_label.setText("")
            print("Established connection")
            if self.client.login == "Invalid Username or Password":
                self.error_label.setText(self.client.login)
        else:  # not connected
            self.error_label.setText("Can't connect to server!")
        self.statusbar.showMessage("Connecting...")
        self.error_label.adjustSize()

    def on_connect(self):
        self.hub = Hub(self.client, self.user.text(), self.Window_Size)
        self.hub.show()
        self.close()

    def on_login_failed(self):
        self.error_label.setText("Failed to Login")
    def update_setting(self, username, host):
        setting = settings.get_standard_settings()
        setting["host"] = self.host.text()
        setting["username"] = self.user.text()
        settings.update_standard_settings(setting)
        self.ask_to_update.close()

    def quit(self):
        self.ask_to_update.close()


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


class Hub(QMainWindow):
    def __init__(self, client, username, WindowSize = WINDOW_SIZE):
        super().__init__()
        self.currentReceiver = "Global Chat"
        self.username = username
        self.players = None
        if self.players == None:
            self.players = [username]
        self.client = client
        self.client.on_players = self.update_players
        self.status = ["online", "online", "online", "online"]
        self.user = self.players[self.players.index(username)]
        self.user_stats = ["1", "1", "1", "1"]
        self.status[self.players.index(self.user)] = "self"
        print(self.status)
        self.starting_height, self.starting_width = 175, 500
        self.difference = 100
        self.line_starting_height = 250
        self.chatBar = "passive"
        self.layout = QHBoxLayout()
        self.chatDictionary = {}
        self.chatListDictionary = {}
        self.playerbuttonlist = []
        self.client.on_global_chat = self.receive_global
        self.client.on_private_chat = self.receive_private
        self.client.on_info = self.tournament_info
        self.labels = []
        self.new_message_list = ["Global Chat"]
        self.Window_Size = WindowSize
        self.initUI()

    def initUI(self):
        for label in self.labels:
            label.deleteLater()
        self.mdi = QMdiArea
        self.statusBar()
        self.statusBar().setStyleSheet("color:white")
        self.statusBar().showMessage("Initialising")

        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(QPixmap("resources/background.png")))
        self.setPalette(palette)

        heading_w, heading_h = self.Window_Size[1] * 0.03, self.Window_Size[0] * 0.03
        heading = QLabel("Hub", self)
        heading.setStyleSheet("QLabel {font-size: 80px; color:white}")
        heading.move(heading_h, heading_w)
        heading.adjustSize()

        self.new_game = PicButton(QPixmap("resources/play.png"), QPixmap("resources/pause.png"),
                                QPixmap("resources/wall.png"), QPixmap("resources/muted.png"), self)
        self.new_game.move(self.Window_Size[1] * 0.05, self.Window_Size[0] * 0.1666666)
        self.new_game.setToolTip("Start a new game")
        self.new_game.clicked.connect(self.game_challenge)
        self.new_game.setFixedSize(QSize(150, 150))
        self.new_game.setShortcut(QKeySequence("Ctrl+N"))

        self.chat_button = PicButton(QPixmap("resources/chat.png"), QPixmap("resources/chat_hover.png"),
                                QPixmap("resources/chat.png"), QPixmap("resources/chat_hover.png"), self)
        self.chat_button.move(self.Window_Size[1] * 0.05, self.Window_Size[0] * 0.3333333)
        self.chat_button.setToolTip("Chat with an online user")
        self.chat_button.clicked.connect(self.choose_chat_user)
        self.chat_button.setFixedSize(QSize(150, 150))
        self.chat_button.setShortcut(QKeySequence("Ctrl+C"))

        self.settings = PicButton(QPixmap("resources/settings.png"), QPixmap("resources/settings_hover.png"),
                                QPixmap("resources/settings.png"), QPixmap("resources/settings_hover.png"), self)
        self.setToolTip("View Settings")
        self.settings.clicked.connect(self.show_settings)
        self.settings.move(self.Window_Size[1] * 0.05, self.Window_Size[0] * 0.5)
        self.settings.setFixedSize(QSize(150, 150))

        self.button = PicButton(QPixmap("resources/play.png"), QPixmap("resources/pause.png"),
                                QPixmap("resources/wall.png"), QPixmap("resources/muted.png"), self)
        self.button.move(self.Window_Size[0] * 0.7, 20)
        self.button.setToolTip("Message Admin")
        self.button.setFixedSize(QSize(100, 100))

        self.button = PicButton(QPixmap("resources/play.png"), QPixmap("resources/pause.png"),
                                QPixmap("resources/wall.png"), QPixmap("resources/muted.png"), self)
        self.button.move(self.Window_Size[0] * 0.8, 20)
        self.button.setToolTip("Browse AI's")
        self.button.setFixedSize(QSize(100, 100))

        self.join_tournament = PicButton(QPixmap("resources/join_tournament.png"), QPixmap("resources/join_tournament_hover.png"),
                                QPixmap("resources/join_tournament.png"), QPixmap("resources/join_tournament_hover.png"), self)
        self.join_tournament.move(self.Window_Size[0] * 0.9, 20)
        self.join_tournament.setToolTip("Join Tournament")
        self.join_tournament.clicked.connect(self.tournament_info)
        self.join_tournament.setFixedSize(QSize(100, 100))

        self.labels = []
        for player in self.players:
            #TODO: Sort so that user is at the top and ingame players at the bottom
            #TODO: add player status
            print(player)
            statusImage = QLabel(self)
            statusImage.setFixedSize(QSize(32, 32))
            statusPicture = QPixmap(PICTURE_DICT[self.status[self.players.index(player)]])
            myScaledPixmap = statusPicture.scaled(statusImage.size(), Qt.KeepAspectRatio)
            statusImage.setPixmap(myScaledPixmap)
            height, width = self.starting_height + self.difference * self.players.index(player) + 10, self.starting_width - 150
            statusImage.move(width, height)
            print(self.players.index(player))
            label = QLabel(player, self)
            label.setStyleSheet("QLabel {font-size: 40px; color: white}")
            height, width = self.starting_height + (self.difference * self.players.index(player)), self.starting_width
            print(height)
            label.move(width, height)
            label.adjustSize()
            label2 = QLabel(self.user_stats[self.players.index(player)], self)
            label2.setStyleSheet("QLabel {font-size: 40px; color: white}")
            label2.move(1200, height)
            label2.adjustSize()

            self.labels.append(label)
            self.labels.append(label2)
            self.labels.append(statusImage)
        for label in self.labels:
            label.show()
        self.draw_chat("Global Chat")
        setup = settings.get_standard_settings()
        header = "PyBot v{}".format(setup["version"])
        self.setWindowTitle(header)
        self.setWindowIcon(QIcon(ICON_PATH))
        self.setGeometry(300, 300, *self.Window_Size)
        self.setFixedSize(*self.Window_Size)
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
        qp.drawLine(0, 150, self.Window_Size[0], 150)
        qp.drawLine(250, 150, 250, self.Window_Size[1])
        for player in self.players:
            pen = QPen(Qt.white, 2, Qt.SolidLine)
            qp.setPen(pen)
            line_height = self.line_starting_height + self.difference * self.players.index(player)
            qp.drawLine(250, line_height, self.Window_Size[0], line_height)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def quitbtnpressed(self, button):
        if button.text() == "quit":
            app.quit()
        string = "Quitting the application"
        self.statusBar().showMessage(string)

    def receive_global(self, sender, message):
        messageList = self.chatDictionary["Global Chat"]
        new_message = "{}&{}".format(sender, message)
        messageList.append(new_message)
        self.new_message_list.append(sender)
        self.chatDictionary["Global Chat"] = messageList
        self.draw_chat(receiver="Global Chat")

    def receive_private(self, sender, message):
        messageList = self.chatDictionary[sender]
        new_message = "{}&{}".format(sender, message)
        messageList.append(new_message)
        currentMessage = self.message.text()
        self.new_message_list.append(sender)
        self.chatDictionary[sender] = messageList
        self.draw_chat(receiver=self.currentReceiver, message=currentMessage)

    def update_chat(self):
        if self.chatBar == "passive":
            self.chatBar = "active"
            string = "The chat is now {}".format(self.chatBar)
            self.statusBar().showMessage(string)
            self.draw_chat(receiver=self.currentReceiver)
        else:
            self.chatBar = "passive"
            string = "The chat is now {}".format(self.chatBar)
            self.statusBar().showMessage(string)
            self.draw_chat(receiver=self.currentReceiver)

    def draw_chat(self, receiver, message=None):
        self.currentReceiver = receiver
        for playerbutton in self.playerbuttonlist:
            playerbutton.deleteLater()
        self.playerbuttonlist = []
        self.initChatDict()
        #tablist: users that have been chatted to before
        self.tablist = []
        for player in self.chatDictionary.keys():
            if self.chatDictionary[player] != []:
                self.tablist.append(player)
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
            if not self.new_message_list:
                self.chat = PicButton(QPixmap("resources/chat_old_collapsed.png"), QPixmap("resources/chat_old_collapsed.png"),
                                 QPixmap("resources/chat_old_collapsed.png"), QPixmap("resources/chat_old_collapsed.png"),
                                 self)
                self.chat.setFixedSize(QSize(798, 75))
                self.setToolTip("")
                self.chat.clicked.connect(self.update_chat)
                self.chat.move(self.Window_Size[0] - 798, self.Window_Size[1] - 75)
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
                self.chat.move(self.Window_Size[0] - 798, self.Window_Size[1] - 75)
                self.chat.raise_()
                self.chat.show()
        else:
            try:
                #deleting the current receiver as new
                self.new_message_list.remove(receiver)
            except:
                pass
            try:
                #deleting previous items
                self.chat.deleteLater()
                self.message.deleteLater()
                self.send.deleteLater()
                self.heading.deleteLater()
                self.scroll.deleteLater()
                self.playerbutton.deleteLater()
            except:
                pass
            if not self.new_message_list:
                self.chat = PicButton(QPixmap("resources/chat_no_new.png"), QPixmap("resources/chat_no_new.png"),
                                 QPixmap("resources/chat_no_new.png"), QPixmap("resources/chat_no_new.png"),
                                 self)
                self.chat.setFixedSize(QSize(798, 547))
                self.chat.clicked.connect(self.update_chat)
                self.chat.move(self.Window_Size[0] - 798, self.Window_Size[1] - 547)
                self.chat.raise_()

                self.heading = QLabel(receiver, self)
                self.heading.move(self.Window_Size[0] - 550, self.Window_Size[1] - 475)
                self.heading.setStyleSheet("QLabel {color:black; font-size:40px}")
                self.heading.adjustSize()

                self.message = QLineEdit(self)
                self.message.setMaxLength(55)
                self.message.setStyleSheet(
                    "QLineEdit {background: white; font-size: 14px; color: black} QLineEdit:focus "
                    "{background: lightgrey;} QTextEdit:placeholder {color: white;}")
                host_w, host_h = self.Window_Size[0] - 700, self.Window_Size[1] - 100
                self.message.move(host_w, host_h)
                self.message.setPlaceholderText("Message")
                self.message.setFixedSize(QSize(500, 40))
                self.message.raise_()
                if message != None:
                    self.message.setText(message)

                self.send = PicButton(QPixmap("resources/play.png"), QPixmap("resources/play.png"),
                                      QPixmap("resources/play.png"), QPixmap("resources/play.png"), self)
                self.send.setFixedSize(40, 40)
                send_w, send_h = self.Window_Size[0] - 150, self.Window_Size[1] - 100
                self.send.move(send_w, send_h)
                self.send.clicked.connect(lambda ignore, receiver_ = str(receiver):
                                          self.send_message(receiver_, self.message.text()))
                self.send.setShortcut(QKeySequence("Return"))
                self.scroll = QScrollArea(self)
                self.scroll.setStyleSheet("QScrollArea {background:white; border:1px dotted grey}")
                self.scroll.move(self.Window_Size[0] - 700, self.Window_Size[1] - 400)
                self.scroll.setFixedSize(590, 250)
                self.scroll.raise_()

                self.playerbuttonlist = []
                for i in range(0, len(self.tablist)):
                    self.playerbutton = QPushButton(self.tablist[i], self)
                    width, height = 798/len(self.tablist), 30
                    self.playerbutton.setFixedSize(width, height)
                    self.playerbutton.move(self.Window_Size[0] - width * (i + 1), self.Window_Size[1] - height)
                    self.playerbutton.setStyleSheet("QPushButton {background:lightgrey; border-radius:0px} "
                                                    "QPushButton:hover {background:darkgrey}")
                    self.playerbutton.clicked.connect(lambda ignore, receiver=self.tablist[i]:
                                                      self.draw_chat(receiver))
                    self.playerbutton.show()
                    if self.tablist[i] == receiver:
                        self.playerbutton.setEnabled(False)
                        self.playerbutton.setStyleSheet("QPushButton {background:grey; border-radius:0px;color:white}")
                    self.playerbuttonlist.append(self.playerbutton)

                scrollContent = QWidget(self.scroll)
                scrollContent.setStyleSheet("QWidget {background:white}")
                scrollLayout = QVBoxLayout(scrollContent)
                scrollContent.setLayout(scrollLayout)
                scrollLayout.setSpacing(0)
                message_list = reversed(self.chatDictionary[receiver])
                for message in message_list:
                    sender, real_message = message.split('&', 1) #The 1 is necessary to prevent unpacking to many vals.
                    if sender != self.user:
                        real_message = "".join([sender, ": ", real_message])
                        messageLabel = QLabel(real_message)
                        messageLabel.setWordWrap(True)
                        messageLabel.setStyleSheet("QLabel {background:white;font-size:14px;}")
                        messageLabel.setAlignment(Qt.AlignLeft)
                        messageLabel.setFixedSize(550, 30)
                        messageLabel.setMaximumWidth(550)
                    else:
                        real_message = "".join([self.user, ": ", real_message])
                        messageLabel = QLabel(real_message)
                        messageLabel.setFixedSize(550, 30)
                        messageLabel.setStyleSheet("QLabel {background:white;font-size:14px;}")
                        messageLabel.setAlignment(Qt.AlignRight)
                    scrollLayout.addWidget(messageLabel, 0)
                self.scroll.setWidget(scrollContent)
                self.scroll.setWidgetResizable(False)
                self.message.setFocus()
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
                self.chat.move(self.Window_Size[0] - 798, self.Window_Size[1] - 547)
                self.chat.raise_()

                self.heading = QLabel(receiver, self)
                self.heading.move(self.Window_Size[0] - 550, self.Window_Size[1] - 475)
                self.heading.setStyleSheet("QLabel {color:black; font-size:40px}")
                self.heading.adjustSize()

                self.message = QLineEdit(self)
                self.message.setMaxLength(55)
                self.message.setStyleSheet(
                    "QLineEdit {background: white; font-size: 14px; color: black} QLineEdit:focus "
                    "{background: lightgrey;} QTextEdit:placeholder {color: white;}")
                host_w, host_h = self.Window_Size[0] - 700, self.Window_Size[1] - 100
                self.message.move(host_w, host_h)
                self.message.setPlaceholderText("Message")
                self.message.setFixedSize(QSize(500, 40))
                self.message.raise_()
                if message != None:
                    self.message.setText(message)

                self.send = PicButton(QPixmap("resources/play.png"), QPixmap("resources/play.png"),
                                      QPixmap("resources/play.png"), QPixmap("resources/play.png"), self)
                self.send.setFixedSize(40, 40)
                send_w, send_h = self.Window_Size[0] - 150, self.Window_Size[1] - 100
                self.send.move(send_w, send_h)
                self.send.clicked.connect(lambda ignore, receiver_=str(receiver):
                                          self.send_message(receiver_, self.message.text()))
                self.send.setShortcut(QKeySequence("Return"))
                self.scroll = QScrollArea(self)
                self.scroll.setStyleSheet("QScrollArea {background:white; border:1px dotted grey}")
                self.scroll.move(self.Window_Size[0] - 700, self.Window_Size[1] - 400)
                self.scroll.setFixedSize(590, 250)
                self.scroll.raise_()

                self.playerbuttonlist = []
                for i in range(0, len(self.tablist)):
                    self.playerbutton = QPushButton(self.tablist[i], self)
                    width, height = 798 / len(self.tablist), 30
                    self.playerbutton.setFixedSize(width, height)
                    self.playerbutton.move(self.Window_Size[0] - width * (i + 1), self.Window_Size[1] - height)
                    self.playerbutton.setStyleSheet("QPushButton {background:lightgrey; border-radius:0px} "
                                                    "QPushButton:hover {background:darkgrey}")
                    if self.tablist[i] in self.new_message_list:
                        self.playerbutton.setStyleSheet("QPushButton {background:lightblue: border-radius:0px;} "
                                                        "QPushButton:hover {background:darkblue}")
                    self.playerbutton.clicked.connect(lambda ignore, receiver=self.tablist[i]:
                                                      self.draw_chat(receiver))
                    self.playerbutton.show()
                    if self.tablist[i] == receiver:
                        self.playerbutton.setEnabled(False)
                        self.playerbutton.setStyleSheet("QPushButton {background:grey; border-radius:0px;color:white}")
                    self.playerbuttonlist.append(self.playerbutton)

                scrollContent = QWidget(self.scroll)
                scrollContent.setStyleSheet("QWidget {background:white}")
                scrollLayout = QVBoxLayout(scrollContent)
                scrollContent.setLayout(scrollLayout)
                scrollLayout.setSpacing(0)
                message_list = reversed(self.chatDictionary[receiver])
                for message in message_list:
                    sender, real_message = message.split('&',
                                                         1)  # The 1 is necessary to prevent unpacking to many vals.
                    if sender != self.user:
                        real_message = "".join([sender, ": ", real_message])
                        messageLabel = QLabel(real_message)
                        messageLabel.setWordWrap(True)
                        messageLabel.setStyleSheet("QLabel {background:white;font-size:14px;}")
                        messageLabel.setAlignment(Qt.AlignLeft)
                        messageLabel.setFixedSize(550, 30)
                        messageLabel.setMaximumWidth(550)
                    else:
                        real_message = "".join([self.user, ": ", real_message])
                        messageLabel = QLabel(real_message)
                        messageLabel.setFixedSize(550, 30)
                        messageLabel.setStyleSheet("QLabel {background:white;font-size:14px;}")
                        messageLabel.setAlignment(Qt.AlignRight)
                    scrollLayout.addWidget(messageLabel, 0)
                self.scroll.setWidget(scrollContent)
                self.scroll.setWidgetResizable(False)
                self.message.setFocus()
                self.chat.show()
                self.message.show()
                self.send.show()
                self.heading.show()
                self.show()
                self.scroll.show()

    def choose_chat_user(self):
        chatable_user = ['Global Chat']
        for i in range(0, len(self.players)):
            if self.status[i] == "online":
                if self.players[i] != self.user:
                    chatable_player = self.players[i]
                    chatable_user.append(chatable_player)
        self.chat_choose_window = QDialog(self)
        chat_choose_width = 300
        chat_choose_height = 300
        self.chat_choose_window.setGeometry(300, 300, chat_choose_height, chat_choose_width)
        self.chat_choose_window.setWindowTitle("Choose a User")
        for i in range(0, len(chatable_user)):
            user_button = QPushButton(str(chatable_user[i]), self.chat_choose_window)
            user_button.setStyleSheet("QPushButton {background:salmon;color:black;} "
                                           "QPushButton:hover {background:skyblue; color:black;}")
            width, height = chat_choose_width, chat_choose_height/len(chatable_user)
            user_button.setFixedSize(QSize(width, height))
            user_button.move(0, height*i)
            usertext = str(user_button.text())
            user_button.clicked.connect(lambda ignore, text_=str(usertext): self.start_chat(text_))
        self.chat_choose_window.setFixedSize(chat_choose_height, chat_choose_width)
        self.chat_choose_window.show()

    def game_challenge(self):
        playable_user = []
        for i in range(0, len(self.players)):
            if self.status[i] == "online":
                if self.players[i] != self.username:
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
            user_button.clicked.connect(lambda ignore, usertext=usertext: self.start_game(usertext))
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
        self.ok.move(40, 225)
        self.cancel = QPushButton("Cancel", self.new_window)
        self.cancel.setStyleSheet("QPushButton {background: white} QPushButton:hover {background:red; color:white}")
        self.cancel.clicked.connect(self.cancle)
        self.cancel.move(185, 225)
        self.new_window.setModal(True)
        self.new_window.move(500, 500)
        self.new_window.setWindowTitle("Settings")
        self.new_window.setGeometry(500, 500, 300, 300)
        self.new_window.setFixedSize(300, 300)
        self.new_window.show()

    def send_message(self, receiver, message):
        if message is not "":
            self.statusBar().showMessage("Sending message...")
            if receiver != "Global Chat":
                query = "chat {0} {1}".format(receiver, message)
            else:
                query = "chat global {}".format(message)
            messageList = self.chatDictionary[receiver]
            print(self.user)
            new_message = "{}&{}".format(self.username, message)
            messageList.append(new_message)
            self.chatDictionary[receiver] = messageList
            self.draw_chat(receiver=receiver)
            self.client.send(query)
        else:
            self.draw_chat(receiver=receiver)

    def clearStatusBar(self):
        print("clearing...")
        self.statusBar().showMessage("")

    def update_players(self, players):
        self.initChatDict()
        self.players = players
        self.status = ["online", "online", "online", "online"]
        self.user = self.players[self.players.index(self.username)]
        self.user_stats = ["1", "1", "1", "1"]
        self.status[self.players.index(self.user)] = "self"
        self.initUI()

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

    def tournament_dialog(self, tournament, players=None):
        if tournament:
            self.tournament_window = QDialog(self)
            tournament_width = 300
            tournament_height = 300
            self.tournament_window.setGeometry(300, 300, tournament_height, tournament_width)
            """self.chat_choose_window.setWindowTitle("Tournaments")
                user_button = QPushButton(str(chatable_user[i]), self.chat_choose_window)
                user_button.setStyleSheet("QPushButton {background:salmon;color:black;} "
                                          "QPushButton:hover {background:skyblue; color:black;}")
                width, height = chat_choose_width, chat_choose_height / len(chatable_user)
                user_button.setFixedSize(QSize(width, height))
                user_button.move(0, height * i)
                usertext = str(user_button.text())
                user_button.clicked.connect(lambda ignore, text_=str(usertext): self.start_chat(text_))
            self.chat_choose_window.setFixedSize(chat_choose_height, chat_choose_width)
            self.chat_choose_window.show()"""

    def tournament_info(self):
        self.client.send("tournament info")

    def initChatDict(self):
        for player in self.players:
            if not player == self.user:
                try:
                    self.chatDictionary[player]
                except:
                    self.chatDictionary.update({player: []})
        try:
            self.chatDictionary["Global Chat"]
        except:
            self.chatDictionary.update({"Global Chat": []})
