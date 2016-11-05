#!/usr/bin/python
# -*- coding: iso-8859-15 -*-"

import socket_conn
import pickle
import os
import sys
import board
from threading import Thread
import time


class GameServer(socket_conn.Server):

    def __init__(self):
        self.connected_clients = []
        super(GameServer, self).__init__()  # initialize the socket server
        self._running = False
        self.last_time = 0

    def exec_(self):
        self.start()  # starts the socket server

    def run_game(self):
        """Starts a new game and runs it"""
        game_board = board.Board(on_finish=self.stop_game)
        map_ = game_board.start_game([ai_path(c.username) for c in
                                      self.connected_clients])
        info = {}
        info["map"] = map_.compress()
        info["bots"] = {b.team: b.serialize() for b in game_board.bots}
        print("info", info)
        self.send_all(b'init ' + pickle.dumps(info), False)

        self._running = True
        print("Game has started")
        while(self._running and not self.terminated):
            if time.time() - self.last_time > 2:
                update = game_board.on_turn()
                self.send_all(b'update ' + pickle.dumps(update), False)
                self.last_time = time.time()
        print("Game has finished")
        self.send_all("finished")

    def stop_game(self):
        self._running = False

    def on_connect(self, client):
        if len(self.connected_clients) >= 2:
            client.send("Server full!\n")
            client.quit()
            return
        username = client.ask("username")
        if username in [c.username for c in self.connected_clients]:
            client.send("Username already used!")
            client.quit()
            return

        client.username = username
        client.ready = False
        print("{} joined the server".format(client.username))
        self.connected_clients.append(client)
        self.send_all("players {}".format(" ".join([c.username for c in
                                                    self.connected_clients])))

    def on_disconnect(self, client):
        print("{} left the server".format(client.username))
        self.connected_clients.remove(client)
        if self._running and len(self.connected_clients) > 0:
            winner = self.connected_clients[0].username
            print("{} won the game".format(winner))
            self.send_all("{} won".format(winner))
            self._running = False

    def handle_client(self, client, query):
        if query == "start":
            if self._running:
                return "already started"
            if not os.path.isfile(ai_path(client.username)):
                return "no ai selected"  # ai/username_ai.py must exist
            client.ready = True  # this client is ready
            if len(self.connected_clients) == 2:
                if not all(c.ready for c in self.connected_clients):
                    return "not ready"  # not every client ready
                Thread(target=self.run_game).start()
                self.send_all("started")  # start game and inform clients
            else:
                print("Not enough players ({} / 2)"
                      .format(len(self.connected_clients)))
                return "not enough {} 2".format(len(self.connected_clients))
        args = query.split(" ")
        key = args[0]
        if len(args) > 1:
            body = " ".join(args[1:])
        if key == "ai":
            with open(ai_path(client.username), 'w+') as f:
                f.write(body)

    def send_all(self, query, encode=True):
        for client in self.connected_clients:
            print("sending to client", query)
            client.send(query, encode)


def ai_path(username):
    return os.path.join("ai", "{0}_ai.py".format(username))


if __name__ == '__main__':
    server = GameServer()
    server.exec_()
    if '--debug' in sys.argv:
        Thread(target=server.run_game).start()
