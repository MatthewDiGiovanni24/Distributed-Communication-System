import socket

s = socket.socket()
print("Socket successfully created")

port = 1001

# bind socket to port
s.bind(("", port))

# set socket to listen
s.listen(5)


while True:

    # connect with client
    c, addr = s.accept()

    c.send("Thank you for connecting".encode())

    # close connection
    c.close()

    break
