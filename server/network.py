from socket_conn import Server
from threading import Thread


class Network(Server):

    def __init__(self, lobby=None):
        super(Network, self).__init__()
        self.start()
        self.servers = []
        if not lobby:
            self.lobby = Hub(self)
        else:
            print("initializing with", lobby)
            self.lobby = lobby(self)
        self.servers.append(self.lobby)  # server 0 is lobby
        # self.servers.extend([LobbyServer(self) for _ in range(5)])

        self.users = []  # keeps track of users connected to the network

    def on_connect(self, conn):
        username = conn.ask("username")
        if username in [u.name for u in self.users]:
            conn.send("already used")
            conn.quit()
            return
        user = User(conn, username)
        self.users.append(user)
        print("{} joined the network".format(user))
        self.lobby.join(user)

    def on_disconnect(self, conn):
        user = self.find_user_by_conn(conn)
        self.lobby.leave(user)
        self.users.remove(user)
        print("{} left the network".format(user))

    def handle_client(self, client, query):
        user = self.find_user_by_conn(client)
        return user.server.handle_input(user, query)

    def find_user_by_conn(self, conn):
        for user in self.users:
            if user.connection == conn:
                return user
        return None

    def move(self, user, target):
        try:
            if type(target) == int:  # by id
                target = self.servers[target]
            assert target.may_join(user)
        except (IndexError, AssertionError):
            print("Unable to join server")
            return

        if user.server is not None:
            user.server.leave(user)
        user.connection.send("moved {}".format(target.id))
        target.join(user)


class VirtualServer:

    current_id = 0

    def __init__(self, network):
        self.users = []  # list of users "connected" to this server
        self.id = VirtualServer.current_id
        VirtualServer.current_id += 1
        self.network = network

    def __repr__(self):
        return "Server {}".format(self.id)

    def run(self, task):
        t = Thread(target=task)
        t.daemon = True
        t.start()

    def may_join(self, user):
        return True

    def join(self, user):
        self.users.append(user)
        self.on_join(user)
        user.server = self
        print("{} joined {}".format(user, self))
        self.send_all("players {}".format(" ".join([u.name
                                                    for u in self.users])))

    def on_join(self, user):
        pass

    def leave(self, user):
        self.users.remove(user)
        self.on_leave(user)
        user.server = None
        print("{} left {}".format(user, self))
        self.send_all("players {}".format(" ".join([u.name
                                                    for u in self.users])))

    def on_leave(self, user):
        pass

    def kick(self, user):
        self.network.move(user, 0)

    def handle_input(self, user, query):
        args = query.split(" ", 1)
        cmd = args[0]  # first part, telling the action
        body = args[1] if len(args) > 1 else None
        if cmd == "leave":
            self.network.move(user, 0)  # moves to hub
        else:
            return self.on_input(user, cmd, body)

    def on_input(self, user, cmd, body):
        pass

    def send_all(self, query, encode=True):
        for user in self.users:
            user.connection.send(query, encode)


class LobbyServer(VirtualServer):

    def __init__(self, network):
        super(LobbyServer, self).__init__(network)

    def on_input(self, user, cmd, body):
        if cmd == "chat":
            for other in self.users:
                if other == user:
                    continue
                other.connection.send("{}> {}".format(user, body))


class Hub(LobbyServer):

    def on_input(self, user, cmd, body):
        super(Hub, self).on_input(user, cmd, body)
        if cmd == "join":
            try:
                self.network.move(user, int(body))
            except ValueError:
                print("Invalid server id")
        elif cmd == "servers":
            return " ".join([str(s.id) for s in self.network.servers])


class User:

    current_id = 0

    def __init__(self, conn, username):
        self.connection = conn  # used to communicate
        self.name = username
        self.id = User.current_id
        self.server = None
        User.current_id += 1

    def __repr__(self):
        return "User {}".format(self.name)
