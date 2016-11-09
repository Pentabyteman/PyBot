import game
import random
import os
from threading import Thread

TOURNAMENT_AI_DIR = "tournament/ai"
TOURNAMENT_DIR = "tournament/"


class TournamentServer(game.GameServer):

    def __init__(self, network):
        super(TournamentServer, self).__init__(network)

    def start(self, ai1, ai2, finished=None):
        self.run(lambda: self.run_game(ai1, ai2))

    def store(self, user_name, ai_data):
        path = game.ai_path(user_name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w+') as f:
            f.write(ai_data)

    def may_join(self, user):
        return True

    def on_join(self, user):
        pass

    def on_leave(self, user):
        pass

    def on_input(self, user, cmd, body):
        pass

    @property
    def available(self):
        return False  # not available for small battles


class Tournament:

    def __init__(self):
        self.players = []
        self.has_started = False
        self.server = None
        print("New tournament created")

    def join(self, player, ai_data=None):
        self.players.append(player)
        print("{} joined the tournament".format(player))
        if ai_data is None:
            return
        path = self._ai_path(player)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w+') as f:
            f.write(ai_data)

    def leave(self, player):
        self.players.remove(player)
        path = self._ai_path(player)
        if os.path.isfile(path):
            os.remove(path)  # clean up ai file
        print("{} left the tournament".format(player))

    @property
    def info(self):
        return "players {}".format([u.name for u in self.players])

    def start(self, server):
        self.has_started = True
        self.server = server
        t = Thread(target=self.run_tournament)
        t.daemon = True
        t.start()

    def run_tournament(self):
        while len(self.players) > 1:
            couples = join_up(self.players)
            for couple in couples:
                if len(couple) == 1:
                    continue
                # preparation
                points = {u: 0 for u in couple}  # store points
                for player in couple:  # write ai files to game server
                    with open(self._ai_path(player), 'r') as f:
                        self.server.store(player.name,
                                          f.read())

                while all(v < 2 for k, v in points.items()):  # run till winner
                    print("{} vs {}".format(*couple))
                    match = couple.copy()
                    random.shuffle(match)
                    print("Match", match)

                    paths = [game.ai_path(player.name) for player in match]
                    # winner is 0, 1 or None (winning team)
                    winner = self.server.run_game(*paths, kick=False)
                    if winner is not None:
                        points[match[winner]] += 1

                loser = min(points, key=points.get)
                self.leave(loser)

    def _ai_path(self, player):
        return os.path.join(TOURNAMENT_DIR, game.ai_path(player.name))


def join_up(players):
    random.shuffle(players)
    return [players[i:i+2] for i in range(0, len(players), 2)]
