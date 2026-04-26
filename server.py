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

peer_ports = {
    1: [1002, 1003],
    2: [1001, 1003],
    3: [1001, 1002]
}

clients = []
usernames = {}
message_history = []   # stores all messages
seen_messages = set()
lock = threading.Lock()

server_id = "SERVER-" + str(server_number)

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


def send_to_peers(message):
    for peer_port in peer_ports[server_number]:
        try:
            peer = socket.socket()
            peer.connect(("127.0.0.1", peer_port))
            peer.send(("SERVERMSG|" + message).encode())
            peer.close()
        except:
            pass

# heartbeat from leader every 5 seconds
def heartbeat():
    announced = False

    while True:
        time.sleep(5)

        if server_role == "LEADER" and not announced:
            broadcast("[SYSTEM] " + server_id + " is now active as LEADER")
            print(server_id + " is LEADER")
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
                if formatted not in seen_messages:
                    seen_messages.add(formatted)
                    message_history.append(formatted)

            print(formatted)
            broadcast(formatted)
            send_to_peers(formatted)

        except:
            if client in clients:
                clients.remove(client)

            if client in usernames:
                left_user = usernames[client]
                del usernames[client]

                msg = "[SYSTEM] " + left_user + " disconnected"

                print(msg)
                broadcast(msg)
                send_to_peers(msg)

            client.close()
            break

def handle_connection(conn):
    try:
        first = conn.recv(1024).decode().strip()

        if first.startswith("SERVERMSG|"):
            msg = first.replace("SERVERMSG|", "", 1)

            with lock:
                if msg not in seen_messages:
                    seen_messages.add(msg)
                    message_history.append(msg)

                    print("[SYNC] " + msg)
                    broadcast(msg)

            conn.close()
            return

        username = first

        usernames[conn] = username
        clients.append(conn)

        join_msg = "[SYSTEM] " + username + " joined the chat"

        print(join_msg)

        with lock:
            if join_msg not in seen_messages:
                seen_messages.add(join_msg)
                message_history.append(join_msg)

        broadcast(join_msg)
        send_to_peers(join_msg)

        with lock:
            for msg in message_history:
                conn.send((msg + "\n").encode())

        conn.send(
            ("[SYSTEM] Connected to " +
             server_id +
             " (" +
             server_role +
             ")\n").encode()
        )

        thread = threading.Thread(target=handle_client, args=(conn,))
        thread.start()

    except:
        conn.close()

heartbeat_thread = threading.Thread(target=heartbeat, daemon=True)
heartbeat_thread.start()

print(server_id + " running on port " + str(port))

while True:
    client, address = s.accept()
    threading.Thread(target=handle_connection, args=(client,)).start()