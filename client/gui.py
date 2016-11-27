#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

import pygame
import os
from itertools import zip_longest
import string
import time
import board
import tkinter
import window
import dialog
from ui_components import ImageButton, Label, GameLog, FileSelectionWidget,\
    Progressbar, TextInputWidget, Button, ListView,\
    ChatWidget, QueueButton
import settings

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


class Speaker:

    def __init__(self):
        self.muted = False

    def play(self, sound):
        if not self.muted:
            sound.play()


class ServerSelect(window.Window):

    def __init__(self, size, client, setup):
        super(ServerSelect, self).__init__(size)
        self.client = client
        self.info_state = True
        self.setup = setup
        heading_w, heading_h = self.rect.width * 0.3, self.rect.height * 0.1
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
        self.login_widget = TextInputWidget(login_rect, "Username:",
                                            (255, 255, 255, 255),
                                            (40, 40, 40, 255),
                                            30, hint="Enter username",
                                            hintcolor=hintcolor)
        self.login_widget.text = setup["username"]
        self.ui_components.add(self.login_widget)

        pwd_rect = login_rect.copy()
        pwd_rect.top = login_rect.bottom + self.rect.height * 0.01
        self.pwd_widget = TextInputWidget(pwd_rect, "Password:",
                                          (255, 255, 255, 255),
                                          (40, 40, 40, 255),
                                          30, hint="Enter password",
                                          hintcolor=hintcolor)
        self.pwd_widget.text = setup["password"]
        self.ui_components.add(self.pwd_widget)

        server_rect = pwd_rect.copy()
        server_rect.top = pwd_rect.bottom + self.rect.height * 0.01
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
        self.info_btn.clicked = self.show_info
        self.ui_components.add(self.info_btn)
        self.client.on_login_failed = self.login_failed

    def show_info(self, event):
        if self.info_state:
            self.info_state = False
            self.info_label.icon = self.ic_no_info
            self.info_label.text = INFO_TEXT.format(self.setup["version"])
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
        password = self.pwd_widget.text
        server = self.server_widget.text
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
            self.error_label.text = "Invalid server address"
            return

        # IMPORTANT
        self.setup["username"], self.setup["host"] = username, host
        self.setup["password"] = password
        settings.update_standard_settings(self.setup)

        print("connecting with", username, password)
        state = self.client.connect(host, port, username, password)
        if state:  # connected, trying to login
            self.btn_conn.enabled, self.server_widget.enabled = False, False
            self.login_widget.enabled, self.pwd_widget.enabled = False, False
            self.error_label.text = ""
            print("Established connection, waiting ...")
        else:  # not connected, could not reach server
            self.error_label.text = "Can't connect to server!"

    def login_failed(self):
        self.btn_conn.enabled, self.server_widget.enabled = True, True
        self.login_widget.enabled, self.pwd_widget.enabled = True, True
        self.error_label.text = "Invalid username or password!"

    def has_connected(self):
        pass


class HubWindow(window.Window):

    def __init__(self, size, client, setup):
        super(HubWindow, self).__init__(size)
        self.client = client
        self.setup = setup

        quit_rect = pygame.Rect(0, 0, self.rect.width * 0.05,
                                self.rect.width * 0.05)
        img = pygame.image.load("resources/exit.png")
        btn_quit = ImageButton(img, quit_rect)
        btn_quit.clicked = lambda x: self.on_quit()
        self.ui_components.add(btn_quit)

        heading_w, heading_h = self.rect.width * 0.3, self.rect.height * 0.1
        heading_rect = pygame.Rect(self.rect.width * 0.1,
                                   self.rect.height * 0.1,
                                   heading_w, heading_h)
        self.heading = Label("Hub", heading_rect, (255, 255, 255, 255), 90)
        self.ui_components.add(self.heading)

        btn_queue_rect = pygame.Rect(self.rect.width * 0.1,
                                     self.rect.height * 0.2,
                                     self.rect.width * 0.15,
                                     self.rect.height * 0.05)
        btn_queue = QueueButton(btn_queue_rect,
                                self.join_queue,
                                self.leave_queue)
        self.ui_components.add(btn_queue)

        spectate_rect = btn_queue_rect.copy()
        spectate_rect.top = btn_queue_rect.bottom + self.rect.height * 0.02
        btn_spectate = Button("Spectate", spectate_rect, text_size=30)
        btn_spectate.clicked = self.show_spectate
        self.ui_components.add(btn_spectate)

        lblp_rect = pygame.Rect(self.rect.width * 0.7,
                                self.rect.height * 0.05,
                                self.rect.width * 0.25,
                                self.rect.height * 0.05)
        lbl_players = Label("Players", lblp_rect, (255, 255, 255, 255), 30)
        self.ui_components.add(lbl_players)

        lv_rect = pygame.Rect(self.rect.width * 0.71,
                              lblp_rect.bottom + self.rect.height * 0.01,
                              self.rect.width * 0.25,
                              self.rect.height * 0.5)
        self.lv_players = ListView(lv_rect, (255, 255, 255, 255),
                                   text_size=25)
        self.ui_components.add(self.lv_players)

        chat_top = lv_rect.bottom + self.rect.height * 0.02
        chat_rect = pygame.Rect(self.rect.width * 0.5,
                                chat_top,
                                self.rect.width * 0.4,
                                self.rect.height - chat_top)
        self.chat_widget = ChatWidget(chat_rect, (0, 0, 0, 255),
                                      self.client.chat,
                                      self.client.username,
                                      text_size=25)
        self.client.on_recv_chat = self.chat_widget.on_recv
        self.ui_components.add(self.chat_widget)
        self.client.players_changed = self.update_players
        if self.client.players_invalid:
            self.update_players()
            self.client.players_invalid = False
        self.client.on_join_queue = btn_queue.on_join
        self.client.on_leave_queue = btn_queue.on_leave

    def chat(self, text, to="global"):
        self.client.chat(text, to)

    def update_players(self):
        print("update players", self.client.players)
        self.lv_players.entries = [p for p in self.client.players
                                   if self.setup["username"] != p]
        self.chat_widget.setup_selectors(self.lv_players.entries.copy())

    def join_queue(self, *args):
        self.client.send("queue join")

    def leave_queue(self, *args):
        self.client.send("queue leave")

    def show_spectate(self, *args):
        dialog.show(dialog.SpectateDialog(dialog.MEDIUM, self.client))

    def on_quit(self):
        pass


class GamePreparation(window.Window):

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


class GameWindow(window.Window):

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
        self.state = window.Window.STATE_INVALID

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
