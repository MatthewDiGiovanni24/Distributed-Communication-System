# Distributed-Communication-System
CSC 2400 Final Project

Matthew DiGiovanni, Adrian Motaharian, Hunter Mullen

Modern communication systems rely on servers to handle message transfer between users. However, if one of these servers goes down, others need to be able to take its place. In normal chat systems, the down server would result in the entire system being down. In a distributed chat system, multiple servers contain the messages and any can step in if one goes down. Given that it is nearly impossible to guarantee a server that never fails, ensuring the resilience of online communication is essential. Distributed systems provide the scalability, fault tolerance, and performance necessary in the massive digital world that has been built.

The goal of this project is to design and implement a simple distributed communication system. The project will be split into two parts. The first part will focus on the client, which will connect to the servers, send messages, and store received messages. The second part will involve the servers, each of which will store copies of every message sent creating replication within the system. One of the servers will be designated as the leader, responsible for coordinating the system and resolving conflicts. If the leader server goes down, a leader election algorithm will run to create a new leader from the available servers.

In addition to the basic functionality of sending and receiving messages, the system will also focus on ensuring message consistency across all servers. This will involve implementing replication strategies to ensure that all servers maintain up-to-date copies of the messages. The leader server will be responsible for handling conflicts in the case multiple servers attempt to send updates simultaneously. The project will aim to evaluate the system’s performance, measuring factors such as message delivery latency, server load balancing, and system responsiveness under varying conditions.
