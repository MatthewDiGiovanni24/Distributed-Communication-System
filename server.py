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
message_history = []   # stores all messages
lock = threading.Lock()


# send to all clients except itself
def broadcast(message, _client):
    for client in clients:
        if client != _client:
            try:
                client.send(message)
            except:
                pass


# removes disconnected clients
def handle_client(client):
    while True:
        try:
            message = client.recv(1024)
            if not message:
                raise Exception("Client disconnected")
            broadcast(message, client)
        except:
            clients.remove(client)
            client.close()
            break


while True:
    client, address = s.accept()
    print("Client Connected")
    clients.append(client)

    thread = threading.Thread(target=handle_client, args=(client,))
    thread.start()
