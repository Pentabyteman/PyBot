#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

import socket_client
from collections import deque
import pygame
import app
import gui
import dialog
import settings
import updates

BOARD_SIZE = (1017, 1017)
WINDOW_SIZE = (1500, 1017)
ICON_PATH = "resources/pybot_logo_ver4.png"


class Game(app.App):

    def __init__(self, display, setup):
        super(Game, self).__init__(display)
        self.setup = setup
        self.setup_client()
        self.server_view()
        self.dialog = None

    def setup_client(self):
        self.client = GameClient()
        self.client.on_connect = self.lobby_view
        self.client.on_move = self.update_window
        self.client.on_quit = self.quit_server

    def update_window(self, server, state):
        if server == 0:
            self.lobby_view()
        elif server >= 0:
            self.game_view(state)

    def lobby_view(self):
        print("lobby view")
        self.window = gui.HubWindow(WINDOW_SIZE, self.client, self.setup)
        self.window.on_quit = self.quit_server

    def quit_server(self):
        self.client.disconnect()
        self.setup_client()
        self.server_view()

    def server_view(self):
        print("server selection")
        self.window = gui.ServerSelect(WINDOW_SIZE, self.client, self.setup)

    def game_view(self, state):
        if self.client.is_playing or state == "playing":
            self.start_game()
        else:
            self.start_preparation()

    def start_preparation(self):
        self.window = gui.GamePreparation(WINDOW_SIZE, self.client,
                                          has_started=self.start_game)

    def start_game(self):
        self.window = gui.GameWindow(WINDOW_SIZE, BOARD_SIZE,
                                     client=self.client)

    def stop(self, *args):
        super(Game, self).stop(*args)
        self.client.disconnect()

    def on_event(self, event):
        if self.dialog is not None:
            if hasattr(event, 'pos'):
                p = [ev - dial for ev, dial in zip(event.pos, self.dialog_pos)]
                event.pos = p
            self.dialog.on_event(event)
        else:
            self.window.on_event(event)

    def on_tick(self):
        self.window.on_tick()

    def on_render(self):
        self.display.fill((0, 0, 0))
        self.display.blit(self.window.image, (0, 0))
        if self.dialog is not None:
            self.display.blit(self.dialog.image, self.dialog_pos)
        pygame.display.flip()

    def reset_dialog(self):
        self.dialog = None


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
        elif key == "tournament":
            if action == "created":
                self.on_tournament_create()
            elif action == "removed":
                self.on_tournament_remove()
            elif action == "info":
                self.on_tournament_info(query["creator"], query["name"],
                                        query["players"])

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

    def on_tournament_create(self):
        pass

    def on_tournament_remove(self):
        pass

    def on_tournament_info(self, creator, name, players):
        pass

    def chat(self, text, to="global"):
        self.send("chat {} {}".format(to, text))

    def start_game(self):
        print("starting game")
        self.send("start")

    def leave(self):
        self.send("leave")

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


def notify_updates(app, needed):
    if not needed:
        return
    dialog.show(dialog.AlertDialog(dialog.SMALL,
                                   "New version available"))


if __name__ == '__main__':
    display = pygame.display.set_mode(WINDOW_SIZE)
    setup = settings.get_standard_settings()
    info = "Running PyBot {0} on {1}. with Python {2} \n "\
        .format(setup["version"], settings.get_pybot_platform(),
                settings.get_python_version())
    print(info)
    # decorating the python window
    header = "PyBot {}".format(setup["version"])
    pygame.display.set_caption(header)
    icon = pygame.transform.scale(pygame.image.load(ICON_PATH), (32, 32))
    pygame.display.set_icon(icon)
    game = Game(display, setup)
    # Checking for updates
    updates.check_for_updates(setup["version"],
                              finished=lambda avail: notify_updates(game,
                                                                    avail))
    game.exec_()
