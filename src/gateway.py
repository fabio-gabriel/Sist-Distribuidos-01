import socket
import threading
import sys
import os
from table import print_table


class IoTGateway:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = []
        self.running = True

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"Gateway is listening on {self.host}:{self.port}")

        # Daemon thread for picking up user commands
        user_command_thread = threading.Thread(target=self.handle_user_commands)
        user_command_thread.daemon = True  # Set as a daemon thread to exit when the main thread exits
        user_command_thread.start()

        # Main thread for accepting new connections
        while self.running:
            client_socket, client_address = server_socket.accept()
            print(f"Accepted connection from {client_address}")
            self.clients.append(client_socket)
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

    def handle_client(self, client_socket):
        try:
            while self.running:
                data = client_socket.recv(1024)
                if not data:
                    break
                print(f"Received message from client: {data.decode()}")

            self.clients.remove(client_socket)
            client_socket.close()
        except Exception as e:
            print(f"Error handling client: {e}")

    # Broadcast function
    def send_data(self, data):
        try:
            for client_socket in self.clients:
                client_socket.send(data.encode())
        except Exception as e:
            print(f"Error sending data: {e}")

    def handle_user_commands(self):
        while self.running:
            user_input = input("Enter a command (or 'quit' to exit): ")
            if user_input.lower() == "quit":
                print("Closing the gateway...")
                gateway.running = False
                for client in self.clients:
                    client.close()
                os._exit(1)
            elif user_input.lower() == "status":
                # Some code like this to request and print all device statuses
                # status = "\n".join(device.request_data() for device in gateway.devices)
                # Should use the send_data() broadcast function to get all the statuses
                print_table(
                    [
                        ["Device", "Status", "Data"],
                        ["Device 1", "On", 5],
                        ["Device 2", "Standby", 17],
                        ["Device 3", "Off", 1],
                    ]
                )
            elif user_input.lower() == "help":
                commands = {
                    "\nstatus": "Check the current status of the program.",
                    "quit": "Exit the program.",
                    "help": "Display a list of available commands.\n",
                }
                print("\nThese are the available commands:")
                for command, desc in commands.items():
                    print(f"{command}: {desc}")
            elif user_input.lower() == "ping":
                # Send anything to devices
                ping_input = input("Type in the ping message: ")
                self.send_data(ping_input)
            else:
                print("Invalid command. Type help for all commands")


if __name__ == "__main__":
    gateway = IoTGateway("localhost", 8080)
    gateway.start()
