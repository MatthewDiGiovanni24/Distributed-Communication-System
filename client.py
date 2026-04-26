import socket
import threading
import time

servers = [
    ("127.0.0.1", 1001),
    ("127.0.0.1", 1002),
    ("127.0.0.1", 1003)
]

username = input("Enter username: ")
s = None
current_server = 0


def connect():
    global s, current_server

    while True:
        try:
            host, port = servers[current_server]
            print(f"Connecting to {port}...")

            s = socket.socket()
            s.connect((host, port))
            s.send(username.encode())

            print(f"Connected to server {port}")
            return

        except:
            print("Failed.")

            current_server = (current_server + 1) % len(servers)
            time.sleep(2)


def read():
    global s

    while True:
        try:
            msg = s.recv(1024).decode()

            if not msg:
                raise Exception()

            print(msg)

        except:
            print("Server lost. Reconnecting...")
            connect()


def write():
    global s

    while True:
        try:
            msg = input()
            s.send(msg.encode())

        except:
            print("Send failed. Reconnecting...")
            connect()


connect()

threading.Thread(target=read, daemon=True).start()
threading.Thread(target=write).start()