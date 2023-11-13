import socket
import threading
import os
import proto.device_pb2
import json


class IoTGateway:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.devices = {}
        self.clients = {}
        self.device_id = 0  # Counter for the device IDs
        self.client_id = 0  # Counter for client IDs
        self.running = True  # Flag to control main loop

    def start(self):
        # Create and configure the server socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"Gateway is listening on {self.host}:{self.port}")

        # Daemon thread for handling user commands
        user_command_thread = threading.Thread(target=self.handle_user_commands)
        user_command_thread.daemon = True  # Set as a daemon thread to exit when the main thread exits
        user_command_thread.start()

        # Main thread for accepting new connections
        while self.running:
            client_socket, client_address = server_socket.accept()
            print(f"Accepted connection from {client_address}")
            client_thread = threading.Thread(target=self.handle_device, args=(client_socket,))
            client_thread.start()

    def handle_device(self, client_socket):
        # Receive and decode the device type sent by the client
        try:
            device_type = client_socket.recv(1024).decode()

            if device_type == "client":
                client_id = self.client_id
                self.client_id += 1  # Increment the client ID counter

                # Store client information in a dictionary
                self.clients[client_id] = {"socket": client_socket}
                print(f"Assigned Client ID {client_id} to client {client_socket.getpeername()}")

            else:
                device_id = self.device_id
                self.device_id += 1  # Increment the device ID counter

                # Store device information in a dictionary
                self.devices[device_id] = {"socket": client_socket, "type": device_type, "value": None}
                print(f"Assigned Device ID {device_id} to client {client_socket.getpeername()} of type {device_type}")

            while self.running:
                data = client_socket.recv(1024)
                if not data:
                    break
                self.handle_messages(data, device_type, client_socket)

            # Remove the client from the dictionary and close the socket
            del self.devices[device_id]
            client_socket.close()
        except Exception as e:
            print(f"Error handling client: {e}")

    def handle_messages(self, data, device_type, client_socket):
        # Handle messages based on the device type
        message = proto.device_pb2.DeviceMessage()
        message.ParseFromString(data)

        if device_type == "client":
            if message.type == proto.device_pb2.DeviceMessage.MessageType.UPDATE:
                update_message = proto.device_pb2.DeviceMessage()
                update_message.type = proto.device_pb2.DeviceMessage.MessageType.UPDATE

                device_list = {
                    key: {"type": value["type"], "value": value["value"]} for key, value in self.devices.items()
                }
                print(device_list)
                update_message.value = json.dumps(device_list)

                client_socket.send(update_message.SerializeToString())
            else:
                self.devices[message.id]["socket"].send(update_message)

        else:
            update_message = proto.device_pb2.DeviceMessage()
            match self.devices[message.id]["type"]:
                case "airconditioner":
                    update_message.type = proto.device_pb2.DeviceMessage.MessageType.AC
                case "lightbulb":
                    update_message.type = proto.device_pb2.DeviceMessage.MessageType.LIGHT
                case "thermostat":
                    update_message.type = proto.device_pb2.DeviceMessage.MessageType.THERMOSTAT

            update_message.value = message.value
            self.broadcast_clients(data.SerializeToString())

    def send_message(self, device_id):
        # Find the dictionary entry with the matching device ID
        if device_id in self.devices:
            device_info = self.devices[device_id]
            device_socket, device_type = device_info["socket"], device_info["type"]

            if device_type == "airconditioner":
                temperature = input("Type in the air conditioner temperature: ")

                message = proto.device_pb2.DeviceMessage()
                message.type = proto.device_pb2.DeviceMessage.MessageType.AC
                message.value = "set_temperature=" + temperature

                try:
                    device_socket.send(message.SerializeToString())
                except Exception as e:
                    print(f"Error sending status message: {e}")

            elif device_type == "lightbulb":
                switch = input("Switch on/off the lightbulb? (1 for on, 0 for off): ")

                message = proto.device_pb2.DeviceMessage()
                message.type = proto.device_pb2.DeviceMessage.MessageType.LIGHT
                message.value = "set_on=" + switch

                try:
                    device_socket.send(message.SerializeToString())
                except Exception as e:
                    print(f"Error sending status message: {e}")

        else:
            print("Did not find in", self.devices)

    # Broadcast function to send data to all devices
    def broadcast_data(self):
        for device_id, device in self.devices.items():
            device_socket = device["socket"]
            device_type = device["type"]
            try:
                if device_type == "airconditioner":
                    message = proto.device_pb2.DeviceMessage()
                    message.type = proto.device_pb2.DeviceMessage.MessageType.AC
                    message.value = "get_temperature"

                elif device_type == "lightbulb":
                    message = proto.device_pb2.DeviceMessage()
                    message.type = proto.device_pb2.DeviceMessage.MessageType.LIGHT
                    message.value = "get_on"

                    wrapper = proto.device_pb2.LightbulbMessage()
                    wrapper.status.CopyFrom(message)

                device_socket.send(wrapper.SerializeToString())

            except Exception as e:
                print(f"Error sending message to device {device_id}: {e}")

    def broadcast_clients(self, data):
        for client_id, client in self.clients.items():
            client["socket"].send(data)

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
                self.send_message(int(device))

            elif user_input.lower() == "show":
                # Show the list of connected clients
                print(self.devices)

            else:
                print("Invalid command. Type help for all commands")


if __name__ == "__main__":
    gateway = IoTGateway("localhost", 8080)
    gateway.start()  # Start the IoT gateway
