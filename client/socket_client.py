#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

import socket
import struct
import ssl
import pickle
from threading import Thread
import select


class SocketClient:

    def __init__(self):
        self.terminated = False
        self.connected = False
        print("Initialized socket client")

    def connect(self, host, port, username, password):
        try:
            print("Connecting to", host, "with", username, password)
            self.socket = socket.socket()
            self.socket = ssl.wrap_socket(self.socket,
                                          ca_certs='server.crt',
                                          cert_reqs=ssl.CERT_REQUIRED)
            self.username, self.password = username, password
            self.socket.connect((host, port))
            self.start()
            self.connected = True
            return True
        except socket.error:
            print("ERROR: Error while connecting!")
            self.connected = False
            return False

    def start(self):
        print("Client has started")
        Thread(target=self.handle_server).start()

    def disconnect(self):
        print("disconnecting")
        self.connected = False
        self.send("quit")
        self.terminated = True
        self.socket.close()

    def send(self, data):
        try:
            msg = struct.pack('>I', len(data)) + data.encode()
            self.socket.sendall(msg)
        except Exception as e:
            print("ERROR: Error while sending", e)

    def handle_server(self):
        while not self.terminated:
            try:
                read_sockets, write_sockets, in_error = \
                    select.select([self.socket, ], [self.socket, ], [], 5)
            except select.error:
                print("FATAL ERROR: Connection error")
                self.socket.shutdown(2)
                self.socket.close()
            if len(read_sockets) > 0:
                raw_msglen = recvall(self.socket, 4)
                if not raw_msglen:
                    print("Connection closed")
                    self.on_quit()
                    return None
                msglen = struct.unpack('>I', raw_msglen)[0]
                recv = recvall(self.socket, msglen)
                reply = None
                try:
                    data = pickle.loads(recv)
                except Exception as e:
                    print("Error: Unable to load data", e)
                    reply = "error"
                else:
                    if len(data) > 0:
                        reply = self.on_receive(data)
                if len(write_sockets) > 0 and reply:
                    self.socket.send(reply.encode())
        print("finished handling server")

    def on_receive(self, query):
        pass

    def on_quit(self):
        pass


def recvall(sock, n):
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data


if __name__ == '__main__':
    client = SocketClient()
