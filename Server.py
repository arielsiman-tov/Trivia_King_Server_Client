############################################## Imports ##############################################
import socket
import threading
import time
import random
import pandas as pd
import uuid

pd.options.display.max_colwidth = 100


############################################## Helper Functions ##############################################
def generate_bot_name():
    """
    Generate a random unique name for a bot.
    """
    return f'{uuid.uuid4().hex[:8]}'


def dict_to_dataframe(dict_data):
    """
    Convert a dictionary to a Pandas DataFrame-for printing statistics.
    """
    df = pd.DataFrame.from_dict(dict_data, orient='index')
    return df


def print_colors_panda(message):
    """
    Print a message with color formatting suitable for Pandas output.
    """
    colors = '\033[1;36m'
    print(f'{colors}{message}\033[0m')


def print_colors(message):
    """
    Print a message with color formatting.
    """
    colors = '\033[1;35m'
    print(f'{colors}{message}\033[0m')


def get_local_ip():
    """
    Get the local IP address of the machine.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.connect(("10.10.10.10", 8080))
            local_ip = s.getsockname()[0]
        except Exception as e:
            f"Error getting local IP address: {e}"
            local_ip = None
    return local_ip


def find_free_port(start_port, end_port):
    """
    Find a free port within a specified range.
    returns the first free port found within the specified range, or None if no free port is found.
    """
    global IP_ADDRESS
    for port in range(start_port, end_port + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((IP_ADDRESS, port))
                return port

        except OSError as e:
            print(f"Port {port} is already in use. Trying the next port...")
            continue


############################################## Game Quetions ##############################################
olympics_questions = {
    "The Olympic Games originated in ancient Greece.": True,
    "The Olympic rings symbolize the five continents of the world.": True,
    "The Summer and Winter Olympics are held every four years, alternating between each other.": True,
    "The Olympic flame is lit in Olympia, Greece, during the opening ceremony of each Olympics.": True,
    "The first modern Olympic Games were held in Athens, Greece, in 1896.": True,
    "Athletes from all over the world compete in the Paralympic Games immediately after the Olympic Games.": True,
    "The Olympic motto is 'Faster, Higher, Stronger.'": True,
    "Golf is one of the sports included in the Summer Olympics.": True,
    "The Olympic Games were canceled during both World War I and World War II.": True,
    "Tokyo hosted the Olympic Games in 1964 and 2020 (postponed to 2021 due to the COVID-19 pandemic).": True,
    "The Olympic Games include both individual and team sports.": True,
    "The Olympic torch relay precedes the opening ceremony and travels through various cities and countries.": True,
    "The Olympic Games have been held in Israel.": False,
    "The Olympic flag features six colors: blue, yellow, black, green, red, and white.": True,
    "The ancient Olympic Games included only athletic events, such as running and wrestling.": True,
    "The Olympic Village provides accommodations for athletes during the Games.": True,
    "An Israeli athlete has never won an Olympic medal": False,
    "Gymnastics is one of the oldest sports included in the modern Olympic Games.": True,
    "The Olympic Games have been held in Asia more times than in any other continent.": True,
    "The Olympic Games have always included a closing ceremony since their inception.": False,
    "The Olympic Games have never been held in Africa.": False,
    "The Olympic Creed states, 'The most important thing in the Olympic Games is to win.'": False,
    "It is impossible for two athletes to win a gold medal together in the same competition at the Olympics": False,
    "The Olympic Games were first televised in color during the 1972 Munich Olympics.": False,
    "The Olympic Games have never been affected by weather conditions causing any delays.": False,
    "Baseball has been a part of the Summer Olympics since the inception of the modern Games.": False,
    "The Olympic Games have been hosted by fewer than 20 different countries.": False,
    "The Olympic Games were first broadcast on television in the 1950s.": False,
    "The Olympic torch has never been extinguished during the relay.": False,
    "The Olympic Games have never been postponed due to non-political reasons.": False,
    "The Olympic Games have always been held in the month of August.": False,
    "The Olympic Games have never faced controversies over doping scandals.": False,
    "Chess has been an official Olympic sport since the first modern Games.": False,
    "The upcoming Summer Olympics will be held in Paris": True,
    "Israel has never hosted an Olympic Games": True
}

############################################## Global Variables ##############################################

# packets
IP_ADDRESS = None
UDP_PORT = 13117
TCP_PORT = 0
SERVER_NAME = 'TriviaMaster'
MAGIC_COOKIE = b'\xab\xcd\xdc\xba'
OFFER_MESSAGE_TYPE = b'\x02'

# Game data
NAMES = []
CONNECTIONS = []
COUNTER = 0
CON_NAME = {}
ANSWERS = {'True': [], 'False': []}
TCP_SOCKET = None
ROUND = 1
UDP_SOCKET = None
GAME_READY_EVENT = threading.Event()
LOCK = threading.Lock()
# Data to store the statistics
WIN_DATA = {}
QUESTIONS_ANSWERS_DATA = {}
QUESTIONS_DATA = {}


############################################## Statistics Functions ##############################################

def update_question_data(question, answer):
    """
    Update question-answer data with the result of a question.
    statistic about the distribution of answers for a question.
    This function updates the global dictionary QUESTIONS_ANSWERS_DATA with the result of a
    question. If the question already exists in the dictionary, it increments the corresponding
    counters based on whether the answer was correct or not. If the question is new, it adds
    the question to the dictionary and initializes the counters accordingly.

    :param question:the selected question
    :param answer: client/bot answer
    """
    global QUESTIONS_ANSWERS_DATA

    if question in QUESTIONS_ANSWERS_DATA:
        if answer:
            QUESTIONS_ANSWERS_DATA[question]["correct"] += 1
        else:
            QUESTIONS_ANSWERS_DATA[question]["incorrect"] += 1
        QUESTIONS_ANSWERS_DATA[question]["total"] += 1
    else:
        if answer:
            QUESTIONS_ANSWERS_DATA[question] = {"correct": 1, "incorrect": 0, "total": 1}
        else:
            QUESTIONS_ANSWERS_DATA[question] = {"correct": 0, "incorrect": 1, "total": 1}


def update_data_no_winner():
    """
    Update game data when there is no winner.
    This function updates the global dictionary WIN_DATA when there is no winner in a game. It
    increments the 'games_played' counter for each player and calculates the percentage of wins
    based on the total number of games played and games won.
    """
    global WIN_DATA
    global NAMES

    for name, _ in NAMES:
        if name.startswith('BOT:'):
            continue
        if name in WIN_DATA:
            WIN_DATA[name]["games_played"] += 1
        else:
            WIN_DATA[name] = {"games_played": 1, "games_won": 0,
                              "percentage_of_wins": 0, }

    # Calculate the percentage of wins for each player
    for name in WIN_DATA:
        games_played = WIN_DATA[name]["games_played"]
        games_won = WIN_DATA[name]["games_won"]
        WIN_DATA[name]["percentage_of_wins"] = (games_won / games_played) * 100


def update_data(winner):
    """
    Update game data after a game has ended.
    This function updates the global dictionary WIN_DATA after a game has ended. It increments
    the 'games_played' counter for each player and, if there is a winner, increments the
    'games_won' counter for the winner. It also calculates the percentage of wins for each player
    based on the total number of games played and games won.
    param winner: the winner of the game
    """
    global WIN_DATA
    global NAMES

    for name, _ in NAMES:
        if name.startswith('BOT:'):
            continue
        if name in WIN_DATA:
            WIN_DATA[name]["games_played"] += 1
        else:
            WIN_DATA[name] = {"games_played": 1, "games_won": 0,
                              "percentage_of_wins": 0, }
    if not winner.startswith('BOT:'):
        WIN_DATA[winner]["games_won"] += 1
    # Calculate the percentage of wins for each player
    for name in WIN_DATA:
        games_played = WIN_DATA[name]["games_played"]
        games_won = WIN_DATA[name]["games_won"]
        WIN_DATA[name]["percentage_of_wins"] = (games_won / games_played) * 100


def q_data(question):
    """
    Update question data with the occurrence of a question,represent the number of times this question
    was selected randomly.
    param question: selected question
    """
    global QUESTIONS_DATA

    if question in QUESTIONS_DATA:
        QUESTIONS_DATA[question]['total'] += 1
    else:
        QUESTIONS_DATA[question] = {'total': 1}


def print_stats():
    """
    Print statistics related to game data.
    This function prints various statistics related to game data, including the top 3 players
    with the highest percentage of wins, the top 3 most viewed questions, and the top 3 most
    answered correctly questions.
    """
    # print the top 3 players in percentage of wins
    global WIN_DATA
    global QUESTIONS_DATA
    global QUESTIONS_ANSWERS_DATA

    # if the dictionary is not empty 
    if WIN_DATA:
        df = dict_to_dataframe(WIN_DATA)
        df = df.sort_values(by=['percentage_of_wins', 'games_played'], ascending=[False, False])
        print_colors_panda(f'Top 3 players in percentage of wins:\n{df.head(3)}')
        print("\n")

    # print the top 3 viewed question
    df = dict_to_dataframe(QUESTIONS_DATA)
    df = df.sort_values(by='total', ascending=False)
    print_colors_panda(f'Top 3 viewed question:\n{df.head(3)}')
    print("\n")

    # print the top 3 answered question
    df = dict_to_dataframe(QUESTIONS_ANSWERS_DATA)
    df = df.sort_values(by='correct', ascending=False)
    print_colors_panda(f'Top 3 answered question:\n{df.head(3)}')
    print("\n")


############################################## Handle Game Functions ##############################################

def start_game():
    """
    Start the trivia game.
    This function initiates the trivia game by sending team names to all clients, selecting a
    random question, and starting a thread to get answers from each client. After a timeout,
    it ends the current round.
    """
    global CONNECTIONS
    global NAMES

    print_colors("Starting the game!")
    # Shuffle the team names
    team_msg = "Welcome to the Mystic server, where we are answering trivia questions about countries\n"
    # Send team names to all clients
    for name, counter in NAMES:
        team_msg += f'Player {counter} : {name}\n'
    # randomize the question
    question = random.choice(list(olympics_questions.keys()))
    team_msg += f'==\n Question: {question}'
    q_data(question)
    print_colors(team_msg)
    broadcast_message(team_msg)
    for client in CONNECTIONS:
        threading.Thread(target=get_answer, args=(question, client)).start()
    time.sleep(10)
    end_round()


def end_round():
    """
    End the current round of the trivia game.

    This function checks the answers submitted by players, updates game data statistics, and
    either declares a winner, declares no winner, or starts a new round.
    """
    global ROUND
    global ANSWERS

    if len(ANSWERS['True']) == 1:
        update_data(ANSWERS['True'][0])  # winner
        end_game(ANSWERS['True'][0])  # end game with winner
    if len(ANSWERS['True']) == 0 and len(ANSWERS['False']) > 0:
        update_data_no_winner()
        no_winner()
    if len(ANSWERS['True']) == 0 and len(ANSWERS['False']) == 0:  # the previous condition makes empty arrays
        close_game_no_winner()
        start_therads()  # start new game
    else:
        message = ''
        for answer in ANSWERS.keys():
            for name in ANSWERS[answer]:
                if answer == 'True':
                    message += f'{name} Is Correct!\n'
                else:
                    message += f'{name} Is InCorrect!\n'
            print_colors(message)
            broadcast_message_for_active_players(message)
            message = ''
        names_correct = [name for name in ANSWERS['True']]
        ROUND += 1
        start_round(names_correct)


def start_round(names_correct):
    """
    Start a new round of the trivia game.
    This function starts a new round by selecting a random question, sending it to the players,
    and starting a thread to get answers from each player. After a timeout, it ends the
    round.

    param names_correct:A list of player names who answered the previous question correctly.    """
    global ROUND
    global ANSWERS
    global CONNECTIONS

    team_msg = f'Round {ROUND}, played by '
    # Send team names to all clients
    i = 1
    for name in names_correct:
        if i == 1:
            team_msg += f'{name} '
            i += 1
        elif i < len(NAMES):
            team_msg += f'and {name}'
            i += 1
        else:
            team_msg += f'and {name}:\n'
    # randomize the question
    question = random.choice(list(olympics_questions.keys()))
    team_msg += f'\nTrue or false: {question}'
    q_data(question)
    print_colors(team_msg)
    broadcast_message_to_correct_players(team_msg)
    ANSWERS['True'] = []
    ANSWERS['False'] = []
    for client in CONNECTIONS:
        name = CON_NAME[client]
        if name in names_correct:
            threading.Thread(target=get_answer, args=(question, client)).start()
    time.sleep(10)
    end_round()


def get_answer(question, client):
    """
    Get the answer from a client.
    This function receives an answer from a client, checks its validity, and updates the
    ANSWERS dictionary accordingly.
    """
    # get the answer from the client
    global CON_NAME

    client.settimeout(10)
    name = CON_NAME[client]
    try:
        while True:
            answer = client.recv(1024).decode().strip()
            if answer == 'T' or answer == 'Y' or answer == '1' or answer == 't' or answer == 'y':
                answer = True
                check_answer(answer, question, client)
                break
                # count += 1
            elif answer == 'F' or answer == 'N' or answer == '0' or answer == 'n' or answer == 'f':
                answer = False
                check_answer(answer, question, client)
                break
                # count += 1
            else:
                client.send('Invalid Answer!'.encode("utf-8"))
    except Exception as e:
        print_colors(f'Error getting answer from {name}:')
        client.close()


def check_answer(answer, question, conn):
    """
    This function compares the submitted answer to the correct answer for a given question.
    It updates round data based on whether the answer is correct or incorrect in ANSWERS dictionary.
    :param answer: The answer submitted by the player after converting to T/F in get_answer()
    :param question: The question for which the answer is being checked.
    :param conn:The socket connection to the player.
    """
    global ANSWERS
    global CON_NAME

    if answer == olympics_questions[question]:
        update_question_data(question, True)
        ANSWERS['True'].append(CON_NAME[conn])
    else:
        update_question_data(question, False)
        ANSWERS['False'].append(CON_NAME[conn])


def no_winner():
    """
    End the game when no winner is determined.
    This function broadcasts a message indicating that there are no winners and closes the game.
    """
    global ANSWERS

    message = ''
    for answer in ANSWERS.keys():
        for name in ANSWERS[answer]:
            message += f'{name} Is InCorrect!\n'
        broadcast_message_for_active_players(message)
        message = ''
    message = f'Game Over!\nNo Winners!'
    print_colors(message)
    broadcast_message(message)
    ANSWERS['True'] = []
    ANSWERS['False'] = []
    close_game()


def end_game(winner):
    """
    End the game and declare a winner.
    This function broadcasts a message declaring the winner of the game and closes the game.
    """
    global ANSWERS

    message = ''
    for answer in ANSWERS.keys():
        for name in ANSWERS[answer]:
            if answer == 'True':
                message += f'{name} Is Correct! {name} Wins!\n'
            else:
                message += f'{name} Is InCorrect!\n'
        print_colors(message)
        broadcast_message_for_active_players(message)
        message = ''
    message = f'Game Over!\n Congratulations to the winner: {winner}'
    print_colors(message)
    broadcast_message(message)
    ANSWERS['True'] = []
    ANSWERS['False'] = []
    close_game()


def close_game():
    """
    Close the game.
    This function closes all client connections, clears game-related variables, prints game
    statistics, and waits for a few seconds before sending out offer requests for a new game.
    """
    global CONNECTIONS
    global GAME_READY_EVENT
    global ROUND
    global COUNTER
    global NAMES
    global CON_NAME

    ROUND = 1
    COUNTER = 0
    for conn in CONNECTIONS:
        conn.close()
    GAME_READY_EVENT.clear()
    CONNECTIONS = []
    NAMES = []
    CON_NAME = {}
    print_colors("Game over,sending out offer requests...")
    print("\n")
    print_stats()
    time.sleep(3)


def close_game_no_winner():
    """
    Close the game when no winner is determined.
    This function closes all client connections, clears game-related variables, and prepares for
    a new game without declaring a winner.
    """
    global CONNECTIONS
    global GAME_READY_EVENT
    global ROUND
    global COUNTER
    global NAMES
    global CON_NAME

    ROUND = 1
    COUNTER = 0
    for conn in CONNECTIONS:
        conn.close()
    GAME_READY_EVENT.clear()
    CONNECTIONS = []
    NAMES = []
    CON_NAME = {}


############################################## Broadcast messages Functions ##############################################

def broadcast_message_for_active_players(message):
    """
    Broadcast a message to active players who have submitted answers.
    This function broadcasts a message to all active players who have submitted answers during the current round.
    """
    global CONNECTIONS
    global CON_NAME

    for conn in CONNECTIONS:
        if CON_NAME[conn] in ANSWERS['True'] or CON_NAME[conn] in ANSWERS['False']:
            try:
                conn.send(message.encode('utf-8'))
            except Exception as e:
                print_colors(f'Error broadcasting message to {CON_NAME[conn]}: {e}')
                CONNECTIONS.remove(conn)
                CON_NAME.pop(conn)
                conn.close()


def broadcast_message_to_correct_players(message):
    """
    Broadcast a message to players who have submitted correct answers in the previous round and continue
    to the next round(used in start_round())
    """
    global CONNECTIONS
    global CON_NAME

    for conn in CONNECTIONS:
        if CON_NAME[conn] in ANSWERS['True']:
            try:
                conn.send(message.encode('utf-8'))
            except Exception as e:
                print_colors(f'Error broadcasting message to {CON_NAME[conn]}: {e}')
                CONNECTIONS.remove(conn)
                CON_NAME.pop(conn)
                conn.close()


def broadcast_message(message):
    """
    Broadcast a message to all connected players.
    This function sends a message to all players who are currently connected to the server.
    """
    global CONNECTIONS
    global CON_NAME

    for conn in CONNECTIONS:
        try:
            conn.send(message.encode('utf-8'))
        except Exception as e:
            print_colors(f'Error broadcasting message to {CON_NAME[conn]}: {e}')
            CONNECTIONS.remove(conn)
            CON_NAME.pop(conn)
            conn.close()


############################################## Handle Clients Functions ##############################################
def handle_client(conn, addr):
    """
    Handle a client connection.
    This function is responsible for handling a client connection to the server.
    It receives the player's name, assigns a unique identifier to the player,
    and waits for the game to start.
    """
    global COUNTER
    global GAME_READY_EVENT
    global NAMES
    global CON_NAME

    conn.settimeout(10)
    try:
        # receive player name
        name = conn.recv(1024).decode().strip()
        # if name not start with 'BOT:', add the player to the game
        if name.startswith('BOT: '):
            name = f'{name}_{generate_bot_name()}'
        else:
            name = f'{name}_{addr[0]}'
        COUNTER += 1
        NAMES.append((name, COUNTER))
        CON_NAME[conn] = name
        GAME_READY_EVENT.wait()

    except Exception as e:
        print_colors(f'Error handling client {addr}: {e}')
        CONNECTIONS.remove(conn)
        conn.close()


def client_connected():
    """
    Accept a new client connection.
    This function accepts a new client connection and starts a thread to handle it.
    """
    global CONNECTIONS
    global TCP_SOCKET

    conn, addr = TCP_SOCKET.accept()
    CONNECTIONS.append(conn)
    threading.Thread(target=handle_client, args=(conn, addr)).start()  # handle player


def tcp_server():
    """
    Run the TCP server.
    This function runs the TCP server,
    accepting client connections and starting the game when enough players have joined.
    """
    global TCP_SOCKET
    global IP_ADDRESS
    global CONNECTIONS
    global NAMES
    global GAME_READY_EVENT

    while True:
        try:
            client_connected()
            TCP_SOCKET.settimeout(10)  # will go the except , 10 sec from the last player- no conn for 10 sec
        except socket.timeout:
            if len(CONNECTIONS) == 0:
                continue  # search players
            break

    if len(NAMES) >= 1:
        TCP_SOCKET.settimeout(None)
        GAME_READY_EVENT.set()  # start game , flag is set
        start_game()
    else:
        tcp_server()


def broadcast_udp():
    """
    Broadcast UDP messages.
    This function broadcasts UDP messages to discover clients on the network.
    """
    global UDP_SOCKET

    message = MAGIC_COOKIE + OFFER_MESSAGE_TYPE + SERVER_NAME.encode().ljust(32) + TCP_PORT.to_bytes(2, 'big')
    while not GAME_READY_EVENT.is_set():  # until game is started- changed in  tcp_server()
        try:
            number = '255.255.255.255'
            UDP_SOCKET.sendto(message, (
            number, UDP_PORT))  # continue to send connection request every second until game is started
        except Exception as e:
            print_colors(f'Error broadcasting UDP message: {e}')
        time.sleep(1)

    ############################################## Setup Connections Functions ##############################################


def tcp_setup():
    """
    Set up the TCP server.
    This function initializes the TCP server by finding a free port,
    binding the socket to the IP address and port,
    and starting to listen for incoming connections.
    """
    global IP_ADDRESS, TCP_PORT, TCP_SOCKET

    TCP_PORT = find_free_port(1025, 65535)
    TCP_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        TCP_SOCKET.bind((IP_ADDRESS, TCP_PORT))
    except Exception as e:
        print_colors(f"Error binding TCP socket to IP address {IP_ADDRESS}, port {TCP_PORT}")
        exit()
    try:
        TCP_SOCKET.listen(10)
    except Exception as e:
        print_colors("Error listening for incoming connections")
        exit()
    print_colors(f"TCP Server started, listening on IP address {IP_ADDRESS}, port {TCP_PORT}")


def udp_setup():
    """
    Set up the UDP socket.
    This function initializes the UDP socket and enables broadcast for the socket.
    """
    global UDP_SOCKET

    try:
        UDP_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except Exception as e:
        print_colors(f"Error creating UDP socket: {e}")
        exit()
    try:
        UDP_SOCKET.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    except Exception as e:
        print_colors(f"Error enabling broadcast for UDP socket: {e}")
        exit()


def start_therads():
    """
    Start the UDP broadcasting and TCP server threads.
    """
    threading.Thread(target=broadcast_udp).start()
    threading.Thread(target=tcp_server).start()


############################################## Main Function ##############################################
def main():
    global IP_ADDRESS

    IP_ADDRESS = get_local_ip()
    tcp_setup()
    udp_setup()
    start_therads()


if __name__ == '__main__':
    main()
