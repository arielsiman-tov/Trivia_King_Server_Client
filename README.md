# Trivia_King

## Overview
This Trivia Client-Server application is an interactive multiplayer trivia game about the Olympic Games. Players join a central server to answer trivia questions about the Olympic Games. 
The Trivia Game consists of 3 main components:
* **Server:** Manages the game, sends questions to clients, and collects their answers.
* **Client:** Connects to the server, receives questions, sends answers, and displays game messages.
* **Bot:** A specialized client that automatically generates answers during the game.

This app allows an unlimited number of clients/bots to play simultaneously.

## Server Workflow
* **Start:** The server initializes and waits for incoming client connections.
* **Client Connection:** When a client connects, the server sends an offer packet containing game details.
* **Game Setup:** Once a client joins, the server starts the game, sending questions to clients.
* **Answer Collection:** Collects answers from clients and evaluates them.
* **Game End:** the game continues for multiple rounds which are played between all users who answered correctly within 10 seconds, until only 1 player is left standing, and this player wins the game.
  
## Client Workflow
* **Start:** The client starts and listens for server broadcasts offers via UDP in order to find available game sessions.
* **Connection:** On receiving an offer, the client connects to the server using TCP.
* **Game Participation:**
  1. Enter the player's name.
  2. Receives questions from the server.
  3. Send an answer.

* **Game End:** Once answered incorrectly, leaves the game and waits for the start of the next game.

## Bot Workflow
* **Start:** The bot client starts and listens for server broadcasts offers via UDP in order to find available game sessions.
* **Connection:** On receiving an offer, the bot connects to the server using TCP.
* **Automated Answers:** Generates answers automatically during the game.
* **Game End:** Once answered incorrectly, leaves the game and waits for the start of the next game.

## Key Technologies which uesed in the work:
* Python 3
* Socket Programming (UDP and TCP)
* Regular Expressions (regex) and Pandas
* Tkinter - Utilized for the graphical user interface (GUI) components in the client application, specifically for the countdown timer interface.
* ANSI color - Used to make your output fun to read.
 
## How to run & Installing required packages
* **Must install:** socket, random, select, uuid, regex, pandas, tkinter, threading ans time.
* **There are 2 ways to start playing:**
  1. Players can launch the client application. The client app will then automatically detect nearby servers and establish a connection.
  2. Players can launch a bot client application. The  bot client app will then automatically detect nearby servers and establish a connection and then will Generate answers automatically.
     
**note:** Make sure the server application is up and running and accessible within the network where the clients are located.
It is possible to run two servers (or more) at the same time from one computer.

## Conclusion
The Trivia Game showcases networking concepts such as UDP discovery, TCP communication, and server-client interactions. It provides an interactive and automated gaming experience suitable for multiplayer trivia sessions.

## Co-Pilot/GPT
In writing parts of the work (mainly defining the connections between server-client, UDP, TCP and the game management components) we used the Visual Studio Co-Pilot assistent.

**Link to a dedicated “chat” in ChatGPT:**
https://chat.openai.com/share/93a8460b-f034-4d58-917a-7ec8c391259c

We used chat GPT mainly in the parts related to connecting the Tkinter (GUI), and defining the individual use of ANSI colors by using regex to catch complex cases.

