#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

import network
import sys
import tournament
import game


class HubServer(network.Hub):

    def __init__(self, network):
        super(HubServer, self).__init__(network)
        self.queue = []
        self.tourn = None

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
        elif cmd == "tournament":
            if body == "info":
                if self.tourn is None:
                    return
                return "tournament info {}".format(self.tourn.info)
            elif body == "create":
                if self.tourn is not None:
                    return "tournament already existing"
                self.tourn = tournament.Tournament()
            elif body == "remove":
                if self.tourn is None:
                    return
                self.tourn = None
            elif body.startswith("join"):
                if self.tourn is None:
                    return "tournament not existing"
                if self.tourn.has_started:
                    return "tournament already started"
                args = body.split(" ", 1)
                if len(args) <= 1 and not self.network.debug:
                    return "tournament no ai given"
                if not self.network.debug:
                    self.tourn.join(user, args[1])
                else:
                    self.tourn.join(user)
            elif body == "leave":
                if self.tourn is None:
                    return "tournament not existing"
                self.tourn.leave(user)
            elif body == "start":
                if self.tourn is None:
                    return "tournament not existing"
                self.tourn.start(self.network.servers[1])  # tournament server

    def match_queue(self):  # tries to match users in queue
        while len(self.queue) >= 2:
            available_servers = [s for s in self.network.servers if type(s) ==
                                 game.GameServer and s.available]
            if len(available_servers) < 1:
                break
            game_server = available_servers[0]
            for _ in range(2):  # get first 2
                self.network.move(self.queue[0], game_server)  # move
                del self.queue[0]  # delete from queue


if __name__ == '__main__':
    if '--debug' in sys.argv:
        debug = True
    nw = network.Network(HubServer, debug)
    tourn_server = tournament.TournamentServer(nw)
    nw.servers.append(tourn_server)
    game_server = game.GameServer(nw)
    nw.servers.append(game_server)

    if debug:
        name1, ai1, name2, ai2 = sys.argv[2:6]
        for name, ai in ((name1, ai1), (name2, ai2)):
            with open(ai, 'r') as f:
                ai_data = f.read()
            dest = ai.split("/")[-1]
            with open(tournament.TOURNAMENT_AI_DIR + "/" + dest, 'w+') as f:
                f.write(ai_data)
