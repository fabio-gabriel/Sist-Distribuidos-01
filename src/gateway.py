import socket
import threading
import os
import proto.device_pb2


class IoTGateway:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = {}
        self.device_id = 0  # Counter for the device IDs
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
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

    def handle_client(self, client_socket):
        # Receive and decode the device type sent by the client
        try:
            device_type = client_socket.recv(1024).decode()

            device_id = self.device_id
            self.device_id += 1  # Increment the device ID counter

            # Store client information in a dictionary
            self.clients[device_id] = {"socket": client_socket, "type": device_type}
            print(f"Assigned Device ID {device_id} to client {client_socket.getpeername()} of type {device_type}")

            while self.running:
                data = client_socket.recv(1024)
                if not data:
                    break
                self.handle_messages(data, device_type)

            # Remove the client from the dictionary and close the socket
            del self.clients[device_id]
            client_socket.close()
        except Exception as e:
            print(f"Error handling client: {e}")

    def handle_messages(self, data, device_type):
        # Handle messages based on the device type
        if device_type == "thermostat":
            message = proto.device_pb2.ThermostatStatus()
            message.ParseFromString(data)

            print(message)

        elif device_type == "airconditioner":
            message = proto.device_pb2.StatusMessage()
            message.ParseFromString(data)

            print(message)

    def send_message(self, device_id):
        # Find the dictionary entry with the matching device ID
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

        elif device_type == "lightbulb":
            switch = input("Switch on/off the lightbulb? (1 for on, 0 for off): ")

            message = proto.device_pb2.LightAction()
            message.action = proto.device_pb2.LightAction.SWITCH
            message.value = str(switch)

            wrapper = proto.device_pb2.LightbulbMessage()
            wrapper.action.CopyFrom(message)

            try:
                device_socket.send(wrapper.SerializeToString())
            except Exception as e:
                print(f"Error sending status message: {e}")

    # Broadcast function to send data to all devices
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

                elif client_type == "lightbulb":
                    message = proto.device_pb2.LightStatus()
                    message.switch = 1

                    wrapper = proto.device_pb2.LightbulbMessage()
                    wrapper.status.CopyFrom(message)

                client_socket.send(wrapper.SerializeToString())

            except Exception as e:
                print(f"Error sending message to device {device_id}: {e}")

    def handle_user_commands(self):
        while self.running:
            user_input = input("Enter a command (or 'quit' to exit): ")
            if user_input.lower() == "quit":
                print("Closing the gateway...")
                self.running = False  # Set the running flag to False
                for device_id, device_info in self.clients.items():
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
                print(self.clients)

            else:
                print("Invalid command. Type help for all commands")


if __name__ == "__main__":
    gateway = IoTGateway("localhost", 8080)
    gateway.start()  # Start the IoT gateway
