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
        try:
            message = s.recv(1024).decode()
            print(message)
        except:
            print("Disconnected from server")
            break


def write():
    while True:
        try:
            msg = input()
            s.send(msg.encode())
        except:
            break


receive_thread = threading.Thread(target=read)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
