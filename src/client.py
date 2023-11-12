import socket
import signal
import threading
import os
import proto.device_pb2
import json
import tkinter as tk
from tkinter import ttk
import time


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = None
        self.running = True  # Flag to control the main loop
        self.devices = {}
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

            receive_thread = threading.Thread(target=self.receive_data)
            receive_thread.daemon = True
            receive_thread.start()

        except Exception as e:
            print(f"Error: {e}")

    def send_device_type(self):
        try:
            # Send the device type as part of the handshake
            self.client_socket.send(self.device_type.encode())
        except Exception as e:
            print(f"Error sending device type: {e}")

    def receive_data(self, callback=None):
        try:
            while self.running:
                data = self.client_socket.recv(1024)
                if not data:
                    break

                gateway_message = proto.device_pb2.DeviceMessage()
                gateway_message.ParseFromString(data)

                if gateway_message.type == proto.device_pb2.DeviceMessage.MessageType.UPDATE:
                    self.devices = json.loads(gateway_message.value)
                    print(self.devices)

                    if callback:
                        callback()

        except Exception as e:
            print(f"Error: {e}")

    def send_data(self):
        message = proto.device_pb2.StatusMessage()
        message.isOn = self.status["isOn"]

        try:
            self.client_socket.send(message.SerializeToString())
        except Exception as e:
            print(f"Error sending status message: {e}")

    def request_update(self):
        update_message = proto.device_pb2.DeviceMessage()
        update_message.type = proto.device_pb2.DeviceMessage.MessageType.UPDATE

        self.client_socket.send(update_message.SerializeToString())

    def send_message(self, device_id):
        # Find the dictionary entry with the matching device ID
        if device_id in self.devices:
            device_info = self.devices[device_id]
            device_type = device_info["type"]

            if device_type == "airconditioner":
                temperature = input("Type in the air conditioner temperature: ")

                message = proto.device_pb2.DeviceMessage()
                message.type = proto.device_pb2.DeviceMessage.MessageType.AC
                message.value = "set_temperature=" + temperature

                try:
                    self.client_socket.send(message.SerializeToString())
                except Exception as e:
                    print(f"Error sending status message: {e}")

            elif device_type == "lightbulb":
                switch = input("Switch on/off the lightbulb? (1 for on, 0 for off): ")

                message = proto.device_pb2.DeviceMessage()
                message.type = proto.device_pb2.DeviceMessage.MessageType.LIGHT
                message.value = "set_on=" + switch

                try:
                    self.client_socket.send(message.SerializeToString())
                except Exception as e:
                    print(f"Error sending status message: {e}")

        else:
            print("Did not find in", self.devices)


class ClientGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Client GUI")
        self.geometry("400x300")

        self.client = Client("localhost", 8080)
        self.client.connect()

        self.create_widgets()

    def create_widgets(self):
        # Treeview for displaying data in a table
        self.tree = ttk.Treeview(self, columns=("ID", "Type"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Type", text="Type")
        self.tree.pack(pady=20)

        # Display initial data in the table
        self.update_table()

        self.command_label = ttk.Label(self, text="Enter a command:")
        self.command_label.pack(pady=10)

        self.command_entry = ttk.Entry(self)
        self.command_entry.pack(pady=10)

        self.submit_button = ttk.Button(self, text="Submit", command=self.process_command)
        self.submit_button.pack(pady=10)

        self.quit_button = ttk.Button(self, text="Quit", command=self.quit_program)
        self.quit_button.pack(pady=10)

    def process_command(self):
        user_input = self.command_entry.get()
        if user_input.lower() == "quit":
            print("Closing the client...")
            self.client.client_socket.close()
            self.quit_program()
        elif user_input.lower() == "status":
            self.client.request_update()
            time.sleep(0.1)
            self.update_table()
        elif user_input.lower() == "update":
            # Send a message to a specific device
            self.client.request_update()
            device = input("Input the device ID: ")
            self.client.send_message(device)
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
        else:
            print("Invalid command. Type help for all commands")

    def quit_program(self):
        self.client.running = False
        os._exit(1)  # Exit the program

    def update_table(self):
        print("i have been called")
        # Clear existing data in the table
        for item in self.tree.get_children():
            self.tree.delete(item)

        print(self.client.devices)

        # Insert data from the dictionary into the table
        for device_id, device_info in self.client.devices.items():
            self.tree.insert("", "end", values=(device_id, device_info["type"]))


if __name__ == "__main__":
    app = ClientGUI()
    app.mainloop()
