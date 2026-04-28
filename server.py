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

server_id = server_number
server_role = "FOLLOWER"
leader_id = None

last_heartbeat = time.time()
election_running = False
message_id = 0


# send to all clients except itself
def broadcast(message, _client=None):
    for client in clients:
        if client != _client:
            try:
                client.send((message + "\n").encode())
            except:
                pass


def send_raw(peer_port, message):
    try:
        peer = socket.socket()
        peer.settimeout(2)
        peer.connect(("127.0.0.1", peer_port))
        peer.send(message.encode())
        peer.close()
        return True
    except:
        return False


def send_to_peers(message):
    for peer_port in peer_ports[server_number]:
        send_raw(peer_port, "SERVERMSG|" + message)

def become_leader():
    global leader_id, server_role

    leader_id = server_id
    server_role = "LEADER"

    print("SERVER-" + str(server_id) + " became LEADER")

    for peer_port in peer_ports[server_number]:
        send_raw(peer_port, "COORDINATOR|" + str(server_id))

    broadcast("[SYSTEM] SERVER-" + str(server_id) + " is now leader")


def start_election():
    global election_running

    if election_running:
        return

    election_running = True

    higher_servers = []

    if server_id == 1:
        higher_servers = [2, 3]
    elif server_id == 2:
        higher_servers = [3]

    got_reply = False

    for sid in higher_servers:
        peer_port = 1000 + sid
        if send_raw(peer_port, "ELECTION|" + str(server_id)):
            got_reply = True

    if not got_reply:
        become_leader()

    election_running = False

def heartbeat():
    global last_heartbeat, leader_id, server_role

    while True:
        time.sleep(2)

        if server_role == "LEADER":
            for peer_port in peer_ports[server_number]:
                send_raw(peer_port, "HEARTBEAT|" + str(server_id))

        else:
            if time.time() - last_heartbeat > 6:
                print("Leader lost. Starting election...")
                leader_id = None
                start_election()

def handle_client(client):
    global message_id
    while True:
        try:
            message = client.recv(1024)
            if not message:
                raise Exception("Client disconnected")
            username = usernames[client]
            text = message.decode()

            if text == "/leader":
                client.send(
                    ("[SYSTEM] Current leader: SERVER-" +
                     str(leader_id) +
                     "\n").encode()
                )
                continue

            if server_role == "LEADER":
                with lock:
                    message_id += 1
                    formatted = f"[{message_id}] {username}: {text}"
            else:
                formatted = f"{username}: {text}"

            with lock:
                if formatted not in seen_messages:
                    seen_messages.add(formatted)
                    message_history.append(formatted)

            print(formatted)
            public = formatted.split("] ", 1)[-1] if formatted.startswith("[") else formatted
            broadcast(public)
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
    global leader_id, server_role, last_heartbeat

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

        if first.startswith("HEARTBEAT|"):
            sender = int(first.split("|")[1])

            leader_id = sender
            last_heartbeat = time.time()

            if sender != server_id:
                server_role = "FOLLOWER"

            conn.close()
            return

        if first.startswith("ELECTION|"):
            sender = int(first.split("|")[1])

            if server_id > sender:
                threading.Thread(target=start_election).start()

            conn.close()
            return

        # new leader announcement
        if first.startswith("COORDINATOR|"):
            leader_id = int(first.split("|")[1])
            server_role = "FOLLOWER"
            last_heartbeat = time.time()

            print("SERVER-" + str(leader_id) + " is LEADER")

            conn.close()
            return

        # normal client connection
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
            ("[SYSTEM] Connected to SERVER-" +
             str(server_id) +
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

threading.Thread(target=start_election, daemon=True).start()
print("SERVER-" + str(server_id) + " running on port " + str(port))

while True:
    client, address = s.accept()
    threading.Thread(target=handle_connection, args=(client,)).start()