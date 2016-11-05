#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

import socket
import struct
from threading import Thread


class Server:

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        host = ''  # localhost
        port = 12345  # just random port
        try:
            self.socket.bind((host, port))
        except socket.error as e:
            print("Error", str(e))

        self.socket.listen(5)
        self.terminated = False

    def start(self):
        Thread(target=self.wait_for_connections).start()

    def wait_for_connections(self):
        while not self.terminated:
            self.accept_connection()

    def accept_connection(self):
        if self.terminated:
            return
        try:
            conn, addr = self.socket.accept()
        except OSError as e:
            print("Error", str(e))
            return
        Thread(target=self.pre_handle_client, args=(conn, addr)).start()

    def clean_up(self):
        self.terminated = True
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()

    def pre_handle_client(self, conn, addr):
        client = ClientConnection(conn)
        self.on_connect(client)

        while not self.terminated:
            text = client.recv()
            if not text:
                break
            print("Received:", text)
            if text.strip() == "quit":
                self.on_disconnect(client)
                break
            elif text.strip() == "terminate":
                self.on_disconnect(client)
                print("Cleaning up")
                self.clean_up()
                break
            reply = self.handle_client(client, text)
            if reply is not None:
                client.send(reply)

        print("Terminating connection")
        client.quit()

    def handle_client(self, query):
        return query

    def on_connect(self, client):
        pass

    def on_disconnect(self, client):
        pass


class ClientConnection:

    def __init__(self, conn):
        self.conn = conn

    def ask(self, question):
        self.send(question)
        return self.recv()

    def recv(self):
        try:
            raw_msglen = recvall(self.conn, 4)
            if not raw_msglen:
                return None
            msglen = struct.unpack('>I', raw_msglen)[0]
            recv = recvall(self.conn, msglen)
            return recv.decode("utf-8")
        except Exception as e:
            print("Error", str(e))
            return None

    def send(self, query, encode=True):
        if encode:
            query = query.encode()
        msg = struct.pack('>I', len(query)) + query
        print("sending message", msg, "len", len(query))
        self.conn.sendall(msg)

    def on_recv(self):
        pass

    def quit(self):
        self.conn.close()


def recvall(sock, n):
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data