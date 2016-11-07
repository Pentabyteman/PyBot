#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

import pygame
import os
from itertools import zip_longest
import string
import time
import board
import tkinter
from ui_components import ImageButton, Label, GameLog, FileSelectionWidget,\
    Progressbar, TextInputWidget, UIGroup, Button
import settings
from PyQt5.QtWidgets import QWidget, QCheckBox, QPushButton, QToolTip, QDesktopWidget, QApplication
from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtGui import QFont
import sys


# prepare file selection dialog
root = tkinter.Tk()
root.withdraw()
# TODO: Valid escape keywords to add @ErichHasl please
INFO_TEXT = """Welcome to PyBot {0}!
This version includes a server implementation.
Please enter username and server address in the two input fields
provided.
If you are having trouble to connect to a server,
make sure that your computer is online and you
have entered the correct server address.

For troubleshooting, please visit
www.github.com/Pentabyteman/PyBot/wiki"""


class Updating_Field(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        qbtn = QPushButton('Update', self)
        qbtn.clicked.connect(self.update)
        QToolTip.setFont(QFont('SansSerif', 10))
        self.setToolTip('This will <b>update</b> your settings')
        qbtn.resize(qbtn.sizeHint())
        qbtn.move(20, 10)

        qbtn = QPushButton("Don't Update", self)
        qbtn.clicked.connect(self.no_update)
        QToolTip.setFont(QFont('SansSerif', 10))
        self.setToolTip("This <b>won't update</b> your settings")
        qbtn.resize(qbtn.sizeHint())
        qbtn.move(160, 10)

        cb_always = QCheckBox('Always Update', self)
        cb_always.move(20, 40)
        cb_always.stateChanged.connect(self.changeAlwaysUpdating)

        cb_never = QCheckBox('Never Update', self)
        cb_never.move(160, 40)
        cb_never.stateChanged.connect(self.changeNeverUpdating)

        self.setGeometry(0, 0, 300, 80)
        self.setWindowTitle('Update Settings')
        self.center()
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def update(self):
        # TODO: How to get user?
        settings.update_standard_settings(host, user)
        QCoreApplication.instance().quit()

    def no_update(self):
        QCoreApplication.instance().quit()


    def changeAlwaysUpdating(self, state):
        if state == Qt.Checked:
            pass
        else:
            pass

    def changeNeverUpdating(selfself, state):
        if state == Qt.Checked:
            pass
        else:
            pass

class Speaker:

    def __init__(self):
        self.muted = False

    def play(self, sound):
        if not self.muted:
            sound.play()


class Window:

    STATE_VALID, STATE_INVALID = 1, 0

    def __init__(self, size):
        self.size = size
        self.rect = pygame.Rect(0, 0, size[0], size[1])
        self.ui_components = UIGroup()
        self.surface = pygame.Surface(self.size)
        self.state = Window.STATE_INVALID

    def draw(self):
        self.surface.fill((0, 0, 0, 0))
        self.ui_components.draw(self.surface)

    @property
    def image(self):
        if self.state == Window.STATE_INVALID:
            self.draw()
            self.state = Window.STATE_VALID
        return self.surface

    def on_tick(self):
        self.ui_components.on_tick()
        self.state = Window.STATE_INVALID

    def on_event(self, event):
        self.ui_components.update(event)
        self.state = Window.STATE_INVALID


class ServerSelect(QWidget, size, client, setup):
    def __init_(self):
        super().__init__()
        self.client = client
        self.info_state = True
        self.setup = setup
        self.heading = Label("PyBot", heading_rect, (255, 255, 255, 255), 90)
        self.initUI()

    def initUI(self, ):
        # TODO: sqaure the images
        self.ic_no_info = pygame.image.load("resources/question.png")
        self.ic_info = pygame.image.load("resources/understood.png")
        self.info_btn = ImageButton(self.ic_no_info, info_btn_rect)
        self.info_btn.clicked = self.show_info
        self.ui_components.add(self.info_btn)

    def show_info(self, event):
        if self.info_state:
            self.info_state = False
            self.info_label.icon = self.ic_no_info
            self.info_label.text = INFO_TEXT.format(self.version)
        else:
            self.info_state = True
            self.info_label.icon = self.ic_info
            self.info_label.text = ""

    def connect(self, event):
        username = self.login_widget.text
        if len(username) < 4 or any(x not in string.ascii_lowercase for x in
                                    username):
            print("Invalid username")
            self.error_label.text = "Invalid username"
            return
        server = self.server_widget.text
        try:
            parts = server.split(":")
            host = parts[0]
            assert len(host) > 0
            if len(parts) > 1:
                port = int(parts[1])
            else:
                port = 12345
        except Exception:
            print("Invalid address", server)
            self.error_label.text = "Invalid server address"
            return

        # IMPORTANT
        if username != self.setup["username"] or host != self.setup["host"]:
            app = QApplication(sys.argv)
            ex = Updating_Field(username, host)
            sys.exit(app.exec_())

        state = self.client.connect(host, port, username)
        if state:  # connected
            self.btn_conn.enabled, self.server_widget.enabled = False, False
            self.login_widget.enabled = False
            self.error_label.text = ""
            print("Established connection")
            self.has_connected()
        else:  # not connected
            self.error_label.text = "Can't connect to server!"

    def has_connected(self):
        pass


class GamePreparation(Window):

    def __init__(self, size, client, has_started):
        super(GamePreparation, self).__init__(size)
        self.client = client
        self.player_labels = []

        lbl_vs_width = self.rect.width * 0.1
        lbl_vs_height = self.rect.height * 0.1
        lbl_vs_rect = pygame.Rect(self.rect.width * 0.5 - lbl_vs_width / 2,
                                  self.rect.height * 0.1,
                                  lbl_vs_width,
                                  lbl_vs_height)
        lbl_vs = Label("vs", lbl_vs_rect, (255, 255, 255, 255), 40)
        self.ui_components.add(lbl_vs)

        lbl_ai_rect = pygame.Rect(self.rect.width * 0.1,
                                  self.rect.height * 0.3,
                                  self.rect.width * 0.3,
                                  self.rect.height * 0.045)
        lbl_ai = Label("Pick your ai file", lbl_ai_rect, (255, 255, 255, 255),
                       40)
        self.ui_components.add(lbl_ai)

        ai_height = self.rect.height * 0.1
        ai_rect = pygame.Rect(lbl_ai_rect.right + self.rect.width * 0.05,
                              lbl_ai_rect.centery - ai_height / 2,
                              self.rect.width * 0.3,
                              ai_height)
        self.ai_selector = FileSelectionWidget(ai_rect)
        self.ai_selector.on_selected = self.select_ai
        self.ui_components.add(self.ai_selector)

        lbl_error_rect = pygame.Rect(lbl_ai_rect.left,
                                     lbl_ai_rect.bottom + self.rect.height *
                                     0.05,
                                     self.rect.width * 0.3,
                                     self.rect.height * 0.045)
        self.lbl_error = Label("", lbl_error_rect, (255, 0, 0, 255),
                               40)
        self.ui_components.add(self.lbl_error)

        # button to start game
        btn_rect = pygame.Rect(lbl_error_rect.left,
                               lbl_error_rect.bottom + self.rect.height * 0.1,
                               self.rect.width * 0.3,
                               self.rect.height * 0.05)
        self.btn_play = Button("Ready to play", btn_rect, 30)
        self.btn_play.clicked = self.play_game
        self.request_start = False
        self.ui_components.add(self.btn_play)

        self.client.started_game = has_started
        self.client.players_changed = self.setup_labels
        if self.client.players_invalid:
            self.setup_labels()
            self.client.players_invalid = False

    def setup_labels(self):
        self.ui_components.remove(s for s in self.ui_components.sprites() if s
                                  in self.player_labels)
        for idx, player in zip_longest(range(2), self.client.players):
            print("adding label", idx, player)

            lbl_player_height = self.rect.height * 0.1
            lbl_player_width = self.rect.width * 0.3
            x_pos = self.rect.width * (0.25 + 0.5 * idx) - lbl_player_width / 2
            lbl_player_rect = pygame.Rect(x_pos,
                                          self.rect.height * 0.1,
                                          lbl_player_width,
                                          lbl_player_height)
            lbl_player = Label(player if player is not None
                               else "Waiting for opponent ...",
                               lbl_player_rect,
                               (255, 0, 0, 255) if idx == 0 else
                               (0, 0, 255, 255),
                               80 if player is not None else 40)
            print("lbl", lbl_player.text, lbl_player.rect)
            self.ui_components.add(lbl_player)
            self.player_labels.append(lbl_player)
        print(len(self.ui_components))

    def select_ai(self):
        if not os.path.isfile(self.ai_selector.path_name):
            self.lbl_error.text = "Invalid ai path"
            return
        print("Sending ai")
        self.client.send_ai(self.ai_selector.path_name)

    def play_game(self, event):
        self.client.send("start")
        self.ai_selector.enabled = False
        self.btn_play.enabled = False


class GameWindow(Window):

    def __init__(self, size, board_size, client, on_finish=None,
                 ai1=None, ai2=None, start=None, speed=False):
        super(GameWindow, self).__init__(size)

        self.speed = speed
        # expects size only to be wider than board_size
        self.board_size = min(board_size, size)  # may not be larger than size
        self.board_pos = [round(0.5 * (s - b))
                          for s, b in zip(self.size, self.board_size)]
        self.on_finish = on_finish

        self.last_time = time.time()
        self.speaker = Speaker()
        self.init_board()

        # calculate some rects for the space available for the gui
        left_space = pygame.Rect(0, 0, self.board_pos[0], self.size[1])
        right_space = pygame.Rect(self.board_pos[0] + self.board_size[0],
                                  self.board_pos[1],
                                  self.board_pos[0],
                                  self.size[1])

        # add a quit button
        quit_btn_rect = pygame.Rect(left_space.width * 0.125,
                                    left_space.height * 0.05,
                                    left_space.width * 0.25,
                                    left_space.width * 0.25)
        ic_quit = pygame.image.load("resources/quit.png")
        quit_btn = ImageButton(ic_quit, quit_btn_rect)
        if on_finish is not None:
            quit_btn.clicked = on_finish
        self.ui_components.add(quit_btn)

        # add a mute button (finally!!)
        mute_btn_rect = pygame.Rect(left_space.width * 0.625,
                                    left_space.height * 0.05,
                                    left_space.width * 0.25,
                                    left_space.width * 0.25)
        self.ic_not_muted = pygame.image.load("resources/not_muted.png")
        self.ic_muted = pygame.image.load("resources/muted.png")
        self.mute_btn = ImageButton(self.ic_not_muted, mute_btn_rect)
        self.mute_btn.clicked = self.mute_sounds
        self.ui_components.add(self.mute_btn)

        # add the button to play/pause the game
        btn_rect = pygame.Rect(left_space.width * 0.1,
                               left_space.height * 0.2,
                               left_space.width * 0.4,
                               left_space.width * 0.4)
        self.ic_play = pygame.image.load("resources/play.png")
        self.ic_pause = pygame.image.load("resources/pause.png")
        self.btn_play = ImageButton(self.ic_play, btn_rect)
        self.btn_play.clicked = self.play
        self.has_started = False

        # button to reset the game
        btn_reset_rect = pygame.Rect(left_space.width * 0.5,
                                     left_space.height * 0.2,
                                     left_space.width * 0.4,
                                     left_space.width * 0.4)
        ic_reset = pygame.image.load("resources/reset.png")
        btn_reset = ImageButton(ic_reset, btn_reset_rect)
        btn_reset.clicked = self.reset
        self.ui_components.add(btn_reset)

        # GameLog
        gameLog_top_x = int(right_space.x + right_space.width * 0.0625)
        gameLog_top_y = int(right_space.height * 0.4)
        gameLog_width = right_space.width * 0.875
        gameLog_height = right_space.height * 0.55
        gamelog_size = (gameLog_width, gameLog_height)
        self.gameLog = GameLog(gamelog_size, gameLog_top_x, gameLog_top_y)

        self.ui_components.add(self.gameLog)

        self.ui_components.add(self.btn_play)

        # socket client to communicate
        self.client = client
        self.client.on_init = lambda init: self.set_initial(init)
        self.client.on_update = lambda update: self.board.update(update)
        self.client.playing_changed = lambda new: self.update_play_icon(new)

        if len(self.client.inits) > 0:
            self.set_initial(self.client.inits.pop())

    def draw(self):
        self.surface.fill((0, 0, 0, 0))  # clean up
        self.surface.blit(self.board.draw(), self.board_pos)
        self.ui_components.draw(self.surface)

    def on_tick(self):
        """Called every tick"""
        super(GameWindow, self).on_tick()
        self.board.on_tick()
        self.state = Window.STATE_INVALID

    def play(self, event):
        self.client.start_game()

    def update_play_icon(self, state):
        self.btn_play.icon = self.ic_pause if state\
            else self.ic_play

    def init_board(self, initial=None):
        self.board = board.Board(self.board_size, initial)
        self.board.speakers = self.speaker

    def reset(self, event):
        self.init_board()
        self.has_started = False
        self.btn_play.icon = self.ic_play
        self.gameLog.reset()

    def mute_sounds(self, event):
        if pygame.mixer.music.get_volume() > 0:
            self.music_volume = pygame.mixer.music.get_volume()
            pygame.mixer.music.set_volume(0)
            self.speaker.muted = True
            self.mute_btn.icon = self.ic_muted
        else:
            pygame.mixer.music.set_volume(self.music_volume)
            self.speaker.muted = False
            self.mute_btn.icon = self.ic_not_muted

    def set_initial(self, initial):
        print("Setting initial setup of game window")
        self.board.set_initial(initial)

        # calculate some rects for the space available for the gui
        right_space = pygame.Rect(self.board_pos[0] + self.board_size[0],
                                  self.board_pos[1],
                                  self.board_pos[0],
                                  self.size[1])

        # list of health bars
        self.health_bars = []

        # stuff specific for each robot
        for idx, bot in enumerate(sorted(self.board.bots,
                                         key=lambda x: x.team)):
            # draw health bars for each robot on the right side of the board
            pb_offset = idx * right_space.height * 0.1
            width, height = right_space.width, right_space.height
            pb_rect = pygame.Rect(right_space.x + width * 0.1,
                                  right_space.y + height * 0.2 + pb_offset,
                                  width * 0.8,
                                  height * 0.05)
            pb_health = Progressbar(pb_rect, bot.team_color(),
                                    [round(x * 0.1)
                                     if i < 3
                                     else x
                                     for i, x in enumerate(bot.team_color())])
            bot.register_health_callback(lambda new, p=pb_health:
                                         p.set_progress(new / bot.maxhealth))
            self.health_bars.append(pb_health)
            self.ui_components.add(pb_health)
