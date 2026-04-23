import socket
import threading
import time

s = socket.socket()
print("Socket successfully created")

server_number = int(input("Server number (1/2/3): "))

if server_number == 1:
    port = 1001
elif server_number == 2:
    port = 1002
else:
    port = 1003

# bind socket to port
s.bind(("", port))

# set socket to listen
s.listen()

clients = []
usernames = {}
message_history = []   # stores all messages
lock = threading.Lock()

server_id = "SERVER-1"

leader_exists = False
server_role = "FOLLOWER"

if not leader_exists:
    server_role = "LEADER"
    leader_exists = True

# send to all clients except itself
def broadcast(message, _client=None):
    for client in clients:
        if client != _client:
            try:
                client.send((message + "\n").encode())
            except:
                pass


# heartbeat from leader every 5 seconds
def heartbeat():
    announced = False

    while True:
        time.sleep(5)

        if server_role == "LEADER" and not announced:
            broadcast("[SYSTEM] " + server_id + " is now active as LEADER")
            announced = True

        if server_role != "LEADER":
            announced = False

# removes disconnected clients
def handle_client(client):
    while True:
        try:
            message = client.recv(1024)
            if not message:
                raise Exception("Client disconnected")
            username = usernames[client]
            text = message.decode()

            if text == "/leader":
                client.send(
                    ("[SYSTEM] Current leader: " + server_id + "\n").encode()
                )
                continue

            formatted = username + ": " + text

            with lock:
                message_history.append(formatted)

            broadcast(formatted)

        except:
            if client in clients:
                clients.remove(client)

            if client in usernames:
                left_user = usernames[client]
                del usernames[client]

                broadcast("[SYSTEM] " + left_user + " disconnected")

            client.close()
            break

heartbeat_thread = threading.Thread(
    target=heartbeat,
    daemon=True
)
heartbeat_thread.start()

while True:
    client, address = s.accept()
    print("Client Connected")

    username = client.recv(1024).decode().strip()
    usernames[client] = username

    clients.append(client)

    broadcast("[SYSTEM] " + username + " joined the chat")

    with lock:
        for msg in message_history:
            client.send(msg.encode())

    client.send(
        ("[SYSTEM] Connected to " +
         server_id +
         " (" +
         server_role +
         ")\n").encode()
    )

    thread = threading.Thread(target=handle_client, args=(client,))
    thread.start()
