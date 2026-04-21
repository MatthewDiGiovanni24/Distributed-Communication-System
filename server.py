import socket
import threading

s = socket.socket()
print("Socket successfully created")

port = 1001

# bind socket to port
s.bind(("", port))

# set socket to listen
s.listen()

clients = []
usernames = {}
message_history = []   # stores all messages
lock = threading.Lock()


# send to all clients except itself
def broadcast(message, _client):
    for client in clients:
        if client != _client:
            try:
                client.send(message.encode())
            except:
                pass


# removes disconnected clients
def handle_client(client):
    while True:
        try:
            message = client.recv(1024)
            if not message:
                raise Exception("Client disconnected")
            username = usernames[client]
            formatted = username + ": " + message.decode()
            with lock:
                message_history.append(formatted)

            broadcast(formatted, client)

        except:
            if client in clients:
                clients.remove(client)
            if client in usernames:
                del usernames[client]
            client.close()
            break


while True:
    client, address = s.accept()
    print("Client Connected")

    username = client.recv(1024).decode()
    usernames[client] = username

    clients.append(client)

    with lock:
        for msg in message_history:
            client.send(msg.encode())

    thread = threading.Thread(target=handle_client, args=(client,))
    thread.start()
