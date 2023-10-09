import socket
import threading
import sys
import os
from table import print_table
import proto.device_pb2


class IoTGateway:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = {}
        self.device_id = 0  # counter for the device ids
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
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

    def handle_client(self, client_socket):
        try:
            device_type = client_socket.recv(1024).decode()

            device_id = self.device_id
            self.device_id += 1  # Increment the device ID counter

            self.clients[device_id] = {"socket": client_socket, "type": device_type}
            print(f"Assigned Device ID {device_id} to client {client_socket.getpeername()} of type {device_type}")

            while self.running:
                data = client_socket.recv(1024)
                if not data:
                    break
                self.handle_messages(data, device_type)

            self.clients.remove(client_socket)
            client_socket["socket"].close()
        except Exception as e:
            print(f"Error handling client: {e}")

    def handle_messages(self, data, device_type):
        if device_type == "thermostat":
            message = proto.device_pb2.ThermostatStatus()
            message.ParseFromString(data)

            print(message)

        elif device_type == "airconditioner":
            message = proto.device_pb2.StatusMessage()
            message.ParseFromString(message)

            print(message)

    def send_message(self, device_id):
        for device_id in self.clients:
            device_type = self.clients[device_id]["type"]
            device_socket = self.clients[device_id]["socket"]

        if device_type == "airconditioner":
            temperature = input("Type in the air conditioner temperature: ")

            message = proto.device_pb2.ActionMessage()
            message.action = proto.device_pb2.ActionMessage.TEMPERATURE
            message.value = str(temperature)

            wrapper = proto.device_pb2.AirConditionerMessage()
            wrapper.action.CopyFrom(message)

            try:
                device_socket.send(wrapper.SerializeToString())
            except Exception as e:
                print(f"Error sending status message: {e}")

    # Broadcast function
    def broadcast_data(self):
        for device_id, device_info in self.clients.items():
            client_socket = device_info["socket"]
            client_type = device_info["type"]
            try:
                if client_type == "airconditioner":
                    message = proto.device_pb2.StatusMessage()
                    message.temperature = 1

                    wrapper = proto.device_pb2.AirConditionerMessage()
                    wrapper.status.CopyFrom(message)

                client_socket.send(wrapper.SerializeToString())

            except Exception as e:
                print(f"Error sending message to device {device_id}: {e}")

    def handle_user_commands(self):
        while self.running:
            user_input = input("Enter a command (or 'quit' to exit): ")
            if user_input.lower() == "quit":
                print("Closing the gateway...")
                gateway.running = False
                for device_id, device_info in self.clients.items():
                    device_info["socket"].close()
                os._exit(1)

            elif user_input.lower() == "status":
                self.broadcast_data()

            elif user_input.lower() == "help":
                commands = {
                    "\nstatus": "Check the current status of the program.",
                    "quit": "Exit the program.",
                    "help": "Display a list of available commands.\n",
                }
                print("\nThese are the available commands:")
                for command, desc in commands.items():
                    print(f"{command}: {desc}")

            elif user_input.lower() == "update":
                device = input("Input the device id: ")
                self.send_message(device)

            elif user_input.lower() == "show":
                print(self.clients)

            else:
                print("Invalid command. Type help for all commands")


if __name__ == "__main__":
    gateway = IoTGateway("localhost", 8080)
    gateway.start()
