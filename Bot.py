import socket
import random
import select
import uuid
import regex as re


UDP_PORT = 13117
BOTS_NAMES = ['BOT: Superman', 'BOT: Spiderman', 'BOT: Ironman', 'BOT: Batman', 'BOT: Wonder Woman',
             'BOT: Captain America', 'BOT: Thor', 'BOT: Black Widow', 'BOT: Hulk', 'BOT: Flash',
             'BOT: Wolverine', 'BOT: Aquaman', 'BOT: Green Lantern', 'BOT: Deadpool', 'BOT: Black Panther',
             'BOT: Doctor Strange', 'BOT: Captain Marvel', 'BOT: Star-Lord', 'BOT: Daredevil', 'BOT: Ant-Man']

class TriviaClient:
    def __init__(self):
        """
        Initialize TriviaClient instance for bot client.
        """
        global UDP_PORT

        self.connected = False  # Flag to indicate whether connected to a server
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp_socket.bind(('', UDP_PORT))
        self.tcp_socket = None

    def print_colors(self, message, flag):
        """
        Print colored message based on the flag.
        :param message:The message to be printed.
        :param flag: Flag to determine the color.
        """
        colors = {
            1: '\033[1;34m',  # Blue
            2: '\033[1;32m',  # Green
            3: '\033[1;93m',  # Yellow
        }
        print(f'{colors.get(flag, "")}{message}\033[0m')

    def generate_bot_name(self):
        """
    Generate a unique name for a bot.
    This method generates a unique name for a bot by concatenating the prefix 'BOT: ' with a
    randomly generated hexadecimal string. The generated name is intended to be unique for each bot instance.
    :return:A unique name for the bot
        """
        return f'BOT: {uuid.uuid4().hex[:8]}'

    def listen_udp(self):
        """
        Listen for UDP packets and process them until connected to a server.
        """
        global BOTS_NAMES
        name = random.choice(BOTS_NAMES)
        self.print_colors(f'{name} started, listening for offer requests...', 1)
        while not self.connected:  # Listen until connected to a server
            ready = select.select([self.udp_socket], [], [], 1)  # Non-blocking check for UDP packet
            if ready[0]:
                data, addr = self.udp_socket.recvfrom(1024)
                # Process UDP packet
                if data.startswith(b'\xab\xcd\xdc\xba\x02'):
                    server_name = data[5:37].strip().decode()
                    server_port = int.from_bytes(data[37:39], 'big')
                    self.tcp_client(addr[0], server_port, server_name, addr, name)

    def tcp_client(self, server_ip, server_port, server_name, addr, name):
        """
    Connect to a server using TCP and handle communication.
    This method establishes a TCP connection to the specified server using the provided IP address
    and port number.The client processes incoming messages from the server, including handling questions,displaying messages, and managing game states.
    The client continuously listens for messages until the connection is terminated and then the client resets its state and begins listening for new
    connection offers.

    :param server_ip:  The IP address of the server to connect to.
    :param server_port:The port number on which the server is listening.
    :param server_name:The name of the server.
    :param addr:ip,port of the server
        """
        try:
            self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_socket.connect((server_ip, server_port))
            self.print_colors(f'Received offer from server "{server_name}" at address {addr[0]}, attempting to connect...',1)
            self.tcp_socket.send(name.encode('utf-8'))
            self.connected = True  # Set connected flag to True
            while self.connected:
                data = self.tcp_socket.recv(1024)
                if not data:
                    break
                    # If the server sends a message that starts with 'Welcome' or 'Round', show the timer window
                pattern1 = r'(.*)(Question:.+)'
                pattern2 = r'(.*)(True or false:.+)'
                match1 = re.search(pattern1, data.decode('utf-8'), re.MULTILINE | re.DOTALL)
                match2 = re.search(pattern2, data.decode('utf-8'), re.MULTILINE | re.DOTALL)
                if match1:
                    sentence_before_question = match1.group(1).strip()
                    self.print_colors(sentence_before_question, 2)
                    sentence_with_question = match1.group(2).strip()
                    self.print_colors(sentence_with_question, 3)
                elif match2:
                    sentence_before_question = match2.group(1).strip()
                    self.print_colors(sentence_before_question, 2)
                    sentence_with_question = match2.group(2).strip()
                    self.print_colors(sentence_with_question, 3)
                else:
                    self.print_colors(data.decode('utf-8'), 2)
                data = data.decode('utf-8')
                if 'Welcome' in data or 'Round' in data or 'Invalid' in data:
                    answer = random.choice(['T', 'Y', '1', 't', 'y', 'F', 'N', '0', 'f', 'n'])
                    self.print_colors(answer,1)
                    self.tcp_socket.send(answer.encode('utf-8'))
                # If the server sends a message that starts with 'Game Over!', close the connection
                if 'Game Over!' in data:
                    self.tcp_socket.close()
                    self.connected = False
                    break
            self.print_colors("Server disconnected, listening for offer requests..",1)
            self.__init__()  # Reset the client after disconnection

        except Exception as e:
            self.print_colors(f'Error connecting to server: {e}',1)
            self.print_colors("Server disconnected, listening for offer requests..",1)
            self.__init__()  # Reset the client after error
def main():
    client = TriviaClient()
    client.listen_udp()

if __name__ == '__main__':
    main()

