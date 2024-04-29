import socket
import select
import threading
import tkinter as tk
import regex as re

UDP_PORT = 13117

class TriviaClient:
    def __init__(self):
        """
        Initialize TriviaClient instance.

        """
        self.connected = False  # Flag to indicate whether connected to a server
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp_socket.bind(('', UDP_PORT))
        self.tcp_socket = None
        self.stop = False
        self.root = None  # Will be initialized later
        self.timer_app = None  # TimerApp instance will be created later
        self.time_up_event = threading.Event()  # Event to signal when time is up

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

    def listen_udp(self):
        """
        Listen for UDP packets and process them until connected to a server.
        """
        self.print_colors('Client started, listening for offer requests...', 1)
        while not self.connected:  # Listen until connected to a server
            ready = select.select([self.udp_socket], [], [], 1)  # Non-blocking check for UDP packet
            if ready[0]:
                data, addr = self.udp_socket.recvfrom(1024)
                # Process UDP packet
                if data.startswith(b'\xab\xcd\xdc\xba\x02'):
                    server_name = data[5:37].strip().decode()
                    server_port = int.from_bytes(data[37:39], 'big')
                    self.tcp_client(addr[0], server_port, server_name, addr)

    def tcp_client(self, server_ip, server_port, server_name, addr):
        """
    Connect to a server using TCP and handle communication.
    This method establishes a TCP connection to the specified server using the provided IP address
    and port number.The client processes incoming messages from the server, including handling questions,displaying messages, and managing game states.
    The client continuously listens for messages until the connection is terminated and then the client resets its state and begins listening for new
    connection offers.

        :param server_ip:  The IP address of the server to connect to.
        :param server_port:The port number on which the server is listening.
        :param server_name:The name of the server.
        :param addr:ip,port of the server.
        """
        try:
            self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_socket.connect((server_ip, server_port))
            self.print_colors(
                f'Received offer from server "{server_name}" at address {addr[0]}, attempting to connect...', 1)
            name = input("Please enter your name: ")
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
                if 'Welcome' in data or 'Round' in data:
                    threading.Thread(target=self.set_countdown).start()  # Start the countdown in a new thread
                    self.get_user_answer_input()
                    self.time_up_event.clear()  # Clear the event for the next round
                if 'Game Over!' in data:
                    self.tcp_socket.close()
                    self.connected = False
                    break
            self.print_colors("Server disconnected, listening for offer requests..", 1)
            self.__init__()  # Reset the client after disconnection

        except Exception as e:
            self.print_colors(f'Error connecting to server: {e}', 1)
            self.print_colors("Server disconnected, listening for offer requests..", 1)
            self.__init__()  # Reset the client after error

    def get_user_answer_input(self):
        """
        Get user's answer input for a question and send it to the server.
        """
        while not self.time_up_event.is_set():
            name = input("Please enter your answer: ")
            if name in ['T', 'Y', '1', 't', 'y', 'F', 'N', '0', 'f', 'n']:
                self.tcp_socket.send(name.encode('utf-8'))
                self.time_up_event.set()  # Set the event to signal time up
                break
            else:
                self.print_colors("Invalid input!", 1)
                self.time_up_event.clear()
                self.get_user_answer_input()

    def set_countdown(self):
        """
        Set up and run the countdown timer app.

        """
        self.root = tk.Tk()
        self.root.title("Countdown Timer")
        self.timer_app = TimerApp(self.root, self.time_up_event)
        self.root.mainloop()  # Start the main loop for the timer app

class TimerApp:
    def __init__(self, master, time_up_event):
        """
        Initialize TimerApp instance.
        """
        self.master = master
        self.master.title("Countdown Timer")
        self.master.geometry("250x100")
        self.remaining_time = 10  # Initial remaining time in seconds
        self.label = tk.Label(self.master, text=f"Time remaining: {self.remaining_time} seconds",
                                font=("Helvetica", 10, "bold"))
        self.label.pack(pady=20, expand=True)
        self.label.config(fg="red")
        self.master.attributes("-topmost", True)  # Make the window stay on top of all others
        self.center_window()
        self.time_up_event = time_up_event  # Event to signal when time is up
        self.start_timer()  # Start the timer automatically

    def center_window(self):
        """
        Center the Tkinter window on the screen.

        """
        self.master.update_idletasks()
        width = self.master.winfo_width()
        height = self.master.winfo_height()
        x = (self.master.winfo_screenwidth() // 2) - (width // 2)
        y = 0
        self.master.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def start_timer(self):
        """
        Start the countdown timer for answering questions.

        """
        if self.remaining_time > 0:
            self.label.config(text=f"Time remaining to answer: {self.remaining_time} seconds",
                              font=("Helvetica", 10, "bold"))
            self.remaining_time -= 1
            self.master.after(1000, self.start_timer)  # Update every 1000 milliseconds (1 second)
        else:
            self.label.config(text="Time's up!")
            self.master.after(1000, self.close_window)  # Schedule close_window after 1 second
            self.time_up_event.set()  # Set the event to signal time up

    def close_window(self):
        """
        Close the timer window.

        """
        self.master.quit()  # Destroy the Tkinter root window

def main():
    client = TriviaClient()
    client.listen_udp()

if __name__ == '__main__':
    main()



