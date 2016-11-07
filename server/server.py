#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

import network
import pickle
import os
import board
import time


class HubServer(network.Hub):

    def __init__(self, network):
        super(HubServer, self).__init__(network)
        self.queue = []

    def on_input(self, user, cmd, body):
        super(HubServer, self).on_input(user, cmd, body)
        if cmd == "queue":
            if body == "join" and user not in self.queue:
                self.queue.append(user)
                if len(self.queue) >= 2:
                    self.match_queue()
            elif body == "leave" and user in self.queue:
                self.queue.remove(user)
            print("Current queue", self.queue)

    def match_queue(self):  # tries to match users in queue
        while len(self.queue) >= 2:
            available_servers = [s for s in self.network.servers if type(s) ==
                                 GameServer and s.available]
            if len(available_servers) < 1:
                break
            game_server = available_servers[0]
            for _ in range(2):  # get first 2
                self.network.move(self.queue[0], game_server)  # move
                del self.queue[0]  # delete from queue


class GameServer(network.VirtualServer):

    def __init__(self, network):
        super(GameServer, self).__init__(network)
        self.last_time = 0
        self._running = False
        self.ready = {}

    def run_game(self):
        """Starts a new game and runs it"""
        game_board = board.Board(on_finish=self.stop_game)
        map_ = game_board.start_game([ai_path(c.name) for c in
                                      self.users])
        info = {}
        info["map"] = map_.compress()
        info["bots"] = {b.team: b.serialize() for b in game_board.bots}
        print("info", info)
        self.send_all(b'init ' + pickle.dumps(info), False)

        self._running = True
        print("Game has started")
        while(self._running):
            if time.time() - self.last_time > 2:
                update = game_board.on_turn()
                self.send_all(b'update ' + pickle.dumps(update), False)
                self.last_time = time.time()
        print("Game has finished")
        self.send_all("finished")
        while len(self.users) > 0:
            self.kick(self.users[0])

    def stop_game(self):
        self._running = False

    def may_join(self, user):
        return len(self.users) < 2

    def on_join(self, user):
        self.ready[user.id] = False

    def on_leave(self, user):
        if self._running and len(self.users) > 0:
            winner = self.users[0].name
            print("{} won the game".format(winner))
            self.send_all("{} won".format(winner))
            self._running = False

    def on_input(self, user, cmd, body):
        if cmd == "start":
            if self._running:
                return "already started"
            if not os.path.isfile(ai_path(user.name)):
                return "no ai selected"  # ai/username_ai.py must exist
            self.ready[user.id] = True
            if len(self.users) == 2:
                if not all(self.ready[c.id] for c in self.users):
                    print("Not ready yet")
                    return "not ready"  # not every user ready
                self.run(self.run_game)
                self.send_all("started")  # start game and inform users
            else:
                print("Not enough players ({} / 2)"
                      .format(len(self.users)))
                return "not enough {} 2".format(len(self.users))
        if cmd == "ai":
            with open(ai_path(user.name), 'w+') as f:
                f.write(body)

    @property
    def available(self):
        return not self._running and len(self.users) < 2


def ai_path(username):
    return os.path.join("ai", "{0}_ai.py".format(username))


if __name__ == '__main__':
    nw = network.Network(HubServer)
    game_server = GameServer(nw)
    nw.servers.append(game_server)
