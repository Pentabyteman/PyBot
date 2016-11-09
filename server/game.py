import network
import pickle
import time
import os
import board


class GameServer(network.VirtualServer):

    def __init__(self, network):
        super(GameServer, self).__init__(network)
        self.last_time = 0
        self._running = False
        self.ready = {}

    def run_game(self, ai1, ai2, kick=True):
        """Starts a new game and runs it"""
        print("game", ai1, ai2)
        game_board = board.Board(on_finish=self.stop_game)
        map_ = game_board.start_game((ai1, ai2))
        info = {}
        info["map"] = map_.compress()
        info["bots"] = {b.team: b.serialize() for b in game_board.bots}
        print("info", info)
        self.send_all(b'init ' + pickle.dumps(info), False)

        self._running = True
        print("Game has started")
        while(self._running):
            if time.time() - self.last_time > 0.5:
                update = game_board.on_turn()
                self.send_all(b'update ' + pickle.dumps(update), False)
                self.last_time = time.time()
        print("Game has finished")
        self.send_all("finished")
        if kick:
            while len(self.users) > 0:
                self.kick(self.users[0])
        return game_board.winner

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
                    return "not ready"
                ai1, ai2 = [ai_path(c.name) for c in self.users]
                self.run(lambda: self.run_game(ai1, ai2))
                self.send_all("started")  # start game and inform users
            else:
                print("Not enough players ({} / 2)"
                      .format(len(self.users)))
                return "not enough {} 2".format(len(self.users))
        if cmd == "ai":
            path = ai_path(user.name)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w+') as f:
                f.write(body)

    @property
    def available(self):
        return not self._running and len(self.users) < 2


def ai_path(username):
    return os.path.join("ai", "{0}_ai.py".format(username))
