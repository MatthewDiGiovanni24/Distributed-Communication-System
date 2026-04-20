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


# send to all clients except itself
def broadcast(message, _client):
    for client in clients:
        if client != _client:
            client.send(message)


# removes disconnected clients
def handle_client(client):
    while True:
        try:
            message = client.recv(1024)
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
