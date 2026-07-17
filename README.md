# Distributed-Communication-System

By Matthew DiGiovanni, Adrian Motaharian, Hunter Mullen

# Version 1.1

Added Lamport logical clocks for message ordering

Added Synchronization of message state on server startup

# Version 1.0

This project is a fault-tolerant distributed messaging system in Python using multithreading and TCP socket programming across replicated servers. Severs contain heartbeats and leader election algorithms to recover from server failures within 8 seconds while maintaining a synchronized message state across nodes.
            
When the servers are live and a client attempts to connect, the client first requests a username. After a name is created the leader server acknowledges the specific user that joined and broadcasts that join message to the system. Once two users are connected either can type messages into their console. These messages are sent through a local socket to the connected server which then broadcasts the message with the other clients and servers. The leader server also continuously checks the connection with the clients and announces disconnections if they appear. An important feature of the system is the ability for clients to reconnect if a server fails. If the connected server crashes or disconnects, the client automatically attempts to connect to another available server from the list of known servers. This process repeats until another server becomes available. 

Every message that is sent is stored in an array within each server. This way, every server has access to the data history in case any of them eventually become the leader. This concept is replication, a “cornerstone mechanism for achieving fault tolerance in distributed systems,” that “can reduce data loss incidents by up to 95.2%,” (Agarwal 3). While this feature does not directly affect the ability of sending and receiving messages, it helps prevent the possibility of losing message history, an essential feature in modern communication systems. After a client sends a message, the leader server distributes each message to the other servers in addition to the other clients allowing for message storage in every server. This allows us to also apply message synchronization. Whenever a new client joins the chat, the server sends previous messages stored in the message history array to the newly connected user. This allows new users to see earlier communication rather than joining an empty chat window. To help prevent repeated messages, the system also tracks messages that have already been received so duplicate broadcasts are avoided.

If the leader server happens to go down, another server takes its place. This is done through a three step process, detecting the down server, electing a new leader, and implementing the new leader. To detect if the leader goes down, every two seconds a heartbeat is sent out to all follower servers from the leader. If a follower does not receive any heartbeat for more than six seconds, it assumes the leader has failed and initiates a new leader election. This time based system represents the concept of a lease, where leadership authority is implicitly valid only for a limited time and must be continuously renewed through periodic heartbeats. If renewal fails, the lease expires and a new leader is elected. This lease concept is “the most widely used leader election mechanism at Amazon,” (Brooker 3).
When initially starting the system, the highest numbered active server becomes the leader. After all servers are connected and the server goes down, the new leader is elected through the Bully Algorithm. The Bully Algorithm functions by simply choosing the next highest available ID among responders to become the new leader. This works by having each server send a message to a higher numbered server, if a server cannot send to a higher server it is highest and becomes the leader. This simple yet effective form of leader election, completes “in an average of 156 milliseconds while consuming 21% of CPU resources during election periods,” (Agarwal 5). The Bully Algorithm creates higher latency but has a lower CPU usage than other common methods of leader election such as the Paxos or Ring Algorithm.
Once the new leader is chosen, it announces itself as leader and an internal flag is flipped to reflect its leadership status. The system treats this server as the coordinator responsible for handling incoming messages and broadcasting them, inheriting all leader functions. An important distinction is that clients do not explicitly track the leader. Instead, they connect to available servers without awareness of which server is currently the leader. Leader status and failure detection are handled entirely within the server layer using coordinator messages and periodic heartbeat signals exchanged between servers. 


Works Cited:

Agarwal, Vedant. “Designing resilient distributed systems: Fault Tolerance Strategies and insights.” INTERNATIONAL JOURNAL OF RESEARCH IN COMPUTER APPLICATIONS AND INFORMATION TECHNOLOGY, vol. 8, no. 1, 31 Jan. 2025, pp. 1102–1113, https://doi.org/10.34218/ijrcait_08_01_082.

Brooker, Marc. "Leader election in distributed systems." Tech. Rep. (2019). https://d1.awsstatic.com/builderslibrary/pdfs/leader-election-in-distributed-systems.pdf
Burns, Brendan. Designing Distributed Systems: Patterns and Paradigms for Scalable, Reliable Services. 2019. https://info.microsoft.com/rs/157-GQE-382/images/EN-CNTNT-eBook-DesigningDistributedSystems.pdf
Fokkink, Wan. Distributed Algorithms: An Intuitive Approach. The MIT Press, 2018.
https://ftp.utcluj.ro/pub/users/civan/CPD/3.RESURSE/8.Book_2015_Fokkink_Distributed%20Algorithms_%20An%20Intuitive%20Approach.pdf

Lamport, Leslie. “Time, clocks, and the ordering of events in a distributed system.” Concurrency: The Works of Leslie Lamport, 9 Oct. 2019, https://doi.org/10.1145/3335772.3335934.

Tanenbaum, Andrew S., and Maarten Van Steen. Distributed Systems: Principles and Paradigms, 2nd Edition. 2014. https://archive.org/details/distributedsyste0000tane_i6v1
“Leader Election in a Distributed System.” GeeksforGeeks, https://www.geeksforgeeks.org/system-design/what-is-leader-election-in-a-distributed-system/.
“Socket Programming in Python.” GeeksforGeeks, https://www.geeksforgeeks.org/python/socket-programming-python/.

