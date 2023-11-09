import socket
import signal
import threading
import os
import proto.device_pb2


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = None
        self.running = True  # Flag to control the main loop
        self.device_type = "client"

    def handle_shutdown(self, signum, frame):
        print("Closing the client...")
        self.running = False
        if self.client_socket:
            self.client_socket.close()

    def connect(self):
        signal.signal(signal.SIGBREAK, self.handle_shutdown)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((self.host, self.port))
            print(f"Connected to {self.host}:{self.port}")
            self.send_device_type()

            receive_thread = threading.Thread(target=self.handle_user_commands)
            receive_thread.daemon = True
            receive_thread.start()

            while self.running:
                data = self.client_socket.recv(1024)
                if not data:
                    break

        except Exception as e:
            print(f"Error: {e}")

    def send_device_type(self):
        try:
            # Send the device type as part of the handshake
            self.client_socket.send(self.device_type.encode())
        except Exception as e:
            print(f"Error sending device type: {e}")

    def send_data(self):
        message = proto.device_pb2.StatusMessage()
        message.isOn = self.status["isOn"]

        try:
            self.client_socket.send(message.SerializeToString())
        except Exception as e:
            print(f"Error sending status message: {e}")

    def handle_user_commands(self):
        while self.running:
            user_input = input("Enter a command (or 'quit' to exit): ")
            if user_input.lower() == "quit":
                print("Closing the gateway...")
                self.running = False  # Set the running flag to False
                for device_id, device_info in self.devices.items():
                    device_info["socket"].close()
                os._exit(1)  # Exit the program

            elif user_input.lower() == "status":
                self.broadcast_data()

            elif user_input.lower() == "help":
                # Display available commands and descriptions
                commands = {
                    "\nstatus": "Check the current status of the program.",
                    "quit": "Exit the program.",
                    "help": "Display a list of available commands.\n",
                }
                print("\nThese are the available commands:")
                for command, desc in commands.items():
                    print(f"{command}: {desc}")

            elif user_input.lower() == "update":
                # Send a message to a specific device
                device = input("Input the device ID: ")
                self.send_message(device)

            elif user_input.lower() == "show":
                # Show the list of connected clients
                print(self.devices)

            else:
                print("Invalid command. Type help for all commands")


if __name__ == "__main__":
    client = Client("localhost", 8080)
    client.connect()

    while client.running:
        user_input = input("Enter data to send to the gateway (or 'quit' to exit): ")
        if user_input.lower() == "quit":
            print("Closing the client...")
            client.client_socket.close()
            break
        elif user_input.lower() == "status":
            print(client.status)
        client.send_data(user_input)

    client.running = False  # Set the running flag to False to exit the receive_data loop