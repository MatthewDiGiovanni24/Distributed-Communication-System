import socket
import threading
import time
import sys

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

    if s is not None:
        try:
            s.close()
        except Exception:
            pass

    while True:
        try:
            host, port = servers[current_server]
            print(f"Connecting to {port}...")

            s = socket.socket()
            s.connect((host, port))
            s.send(username.encode())

            print(f"Connected to server {port}")
            return

        except Exception:
            print("Failed.")

            current_server = (current_server + 1) % len(servers)
            time.sleep(2)


def read():
    global s

    while True:
        try:
            buf = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    raise ConnectionError("Disconnected")
                buf += chunk
                if b"\n" in buf:
                    break

            msg = buf.decode(errors="replace").strip()
            if msg:
                print(msg)
                sys.stdout.flush()

        except Exception:
            print("Server lost. Reconnecting...")
            connect()


def write():
    global s

    while True:
        try:
            msg = input()
            if not msg:
                continue
            s.sendall(msg.encode())

        except Exception:
            print("Send failed. Reconnecting...")
            connect()


connect()

threading.Thread(target=read, daemon=True).start()
threading.Thread(target=write).start()