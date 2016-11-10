import game
import random
import os
from threading import Thread
from itertools import combinations

TOURNAMENT_AI_DIR = "tournament/ai"
TOURNAMENT_DIR = "tournament/"


class TournamentServer(game.GameServer):
    """GameServer only used for tournaments"""

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
    """
    Tournaments are events where many different ai developers can compare their
    skills. Players of the network can join a tournament. When started, several
    matches are played to find the best one.
    """

    def __init__(self, debug=False):
        self.players = []
        self.has_started = False
        self.server = None
        self.debug = debug
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
        print("{} left the tournament".format(player))
        if self.debug:
            return
        path = self._ai_path(player)
        if os.path.isfile(path):
            os.remove(path)  # clean up ai file

    def close(self):
        while len(self.players) > 0:
            self.leave(self.players[0])
        if self.server is not None:
            self.server.kick_all()
        print("Tournament was closed!")

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
        """
        Runs the tournament
        First, until there are less than 5 players left, they are matched up
        against a random opponent. The winner after three matches gets to the
        next round.
        Second, when there are less than 5 players left, everyone fights
        everyone. In the end the player with the most victories wins. If their
        is a tie, the results of their own match decides.
        """
        while len(self.players) > 4:  # k.o phase
            couples = join_up(self.players)
            for couple in couples:
                loser = self.match_up(couple)
                if loser is not None:
                    self.leave(loser)

        # alle gegen alle
        points = {p: 0 for p in self.players}
        for couple in combinations(self.players, 2):
            loser = self.match_up(list(couple))
            winner = next(x for x in couple if x != loser)
            print("{} won against {}".format(winner, loser))
            points[winner] += 1
            print("Point balance: {}".format(points))

        highest = max(points.values())
        final = [pl for pl, po in points.items() if po == highest]
        winner_str = " ".join([p.name for p in final])
        print("{} won the tournament".format(winner_str))
        self.close()

    def _ai_path(self, player):
        return os.path.join(TOURNAMENT_DIR, game.ai_path(player.name))

    def match_up(self, couple):
        """Matchs 2 players up, first to 2 wins, returns loser"""
        if len(couple) == 1:
            return None
        # preparation
        points = {u: 0 for u in couple}  # store points
        for player in couple:  # write ai files to game server
            with open(self._ai_path(player), 'r') as f:
                self.server.store(player.name,
                                  f.read())

        while all(v < 2 for k, v in points.items()):  # run until winner
            print("{} vs {}".format(*couple))
            match = couple.copy()
            random.shuffle(match)
            print("Match", match)

            paths = [game.ai_path(player.name) for player in match]
            # winner is 0, 1 or None (winning team)
            winner = self.server.run_game(*paths, kick=False)
            if winner is not None:
                points[match[winner]] += 1

        return min(points, key=points.get)  # loser


def join_up(players):
    random.shuffle(players)
    return [players[i:i+2] for i in range(0, len(players), 2)]
