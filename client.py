import socket

s = socket.socket()

port = 1001

# connect to server on locally
s.connect(("127.0.0.1", port))

# receive data from server
print(s.recv(1024).decode())

s.close()
