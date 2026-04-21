import socket
import threading

s = socket.socket()

port = 1001

# connect to server on locally
s.connect(("127.0.0.1", port))

username = input("Enter your username: ")
s.send(username.encode())

def read():
    while True:
        message = s.recv(1024).decode()
        print(message)


def write():
    while True:
       msg = input()
       s.send(msg.encode())


receive_thread = threading.Thread(target=read)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
