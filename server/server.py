#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

import network
import pickle
import os
import board
import time


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


def ai_path(username):
    return os.path.join("ai", "{0}_ai.py".format(username))


if __name__ == '__main__':
    nw = network.Network()
    game_server = GameServer(nw)
    nw.servers.append(game_server)
