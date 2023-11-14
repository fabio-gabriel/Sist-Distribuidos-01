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

    def receive_data(self):
        try:
            while self.running:
                data = self.client_socket.recv(1024)
                if not data:
                    break

                gateway_message = proto.device_pb2.DeviceMessage()
                gateway_message.ParseFromString(data)

                if gateway_message.type == 3:
                    self.devices = json.loads(gateway_message.value)
                    print(self.devices)

                else:
                    self.devices[str(gateway_message.id)]["value"] = int(gateway_message.value)
                    print("devices list", self.devices)

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
        self.minsize(700, 500)

        # Treeview for displaying data in a table
        self.tree = ttk.Treeview(self, columns=("ID", "Type", "Value"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Value", text="Value")
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
            time.sleep(0.1)
            self.update_table()
            self.update_popup()
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
        # Clear existing data in the table
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Insert data from the dictionary into the table
        for device_id, device_info in self.client.devices.items():
            self.tree.insert("", "end", values=(device_id, device_info["type"], device_info["value"]))

    def update_popup(self):
        self.popup = tk.Toplevel(self)
        self.popup.title("Update a device")

        self.popup.command_label = ttk.Label(self.popup, text="Enter the device ID: ")
        self.popup.command_label.pack(pady=10)

        self.popup.command_entry = ttk.Entry(self.popup)
        self.popup.command_entry.pack(pady=10)

        self.popup.submit_button = ttk.Button(self.popup, text="Submit", command=self.get_device)
        self.popup.submit_button.pack(pady=10)

    def get_device(self):
        self.user_input = self.popup.command_entry.get()

        for widget in self.popup.winfo_children():
            widget.destroy()

        if self.user_input in self.client.devices:
            device_info = self.client.devices[self.user_input]
            device_type = device_info["type"]

            if device_type == "airconditioner":
                self.popup.command_label = ttk.Label(self.popup, text="Enter the new temperature: ")
                self.popup.command_label.pack(pady=10)

                self.popup.command_entry = ttk.Entry(self.popup)
                self.popup.command_entry.pack(pady=10)

                self.popup.submit_button = ttk.Button(self.popup, text="Submit", command=self.create_AC_message)
                self.popup.submit_button.pack(pady=10)

            elif device_type == "lightbulb":
                self.popup.command_label = ttk.Label(
                    self.popup, text="Switch on/off the lightbulb? (1 for on, 0 for off): "
                )
                self.popup.command_label.pack(pady=10)

                self.popup.command_entry = ttk.Entry(self.popup)
                self.popup.command_entry.pack(pady=10)

                self.popup.submit_button = ttk.Button(self.popup, text="Submit", command=self.create_Light_message)
                self.popup.submit_button.pack(pady=10)

        else:
            print("Did not find in", self.devices)

    def create_AC_message(self):
        user_input = self.popup.command_entry.get()

        message = proto.device_pb2.DeviceMessage()
        message.type = proto.device_pb2.DeviceMessage.MessageType.AC
        message.value = "set_temperature=" + str(user_input)
        message.id = int(self.user_input)

        try:
            self.client.client_socket.send(message.SerializeToString())
            self.client.devices[self.user_input]["value"] = user_input
        except Exception as e:
            print(f"Error sending status message: {e}")

        self.update_table()
        self.popup.destroy()

    def create_Light_message(self):
        user_input = self.popup.command_entry.get()

        message = proto.device_pb2.DeviceMessage()
        message.type = proto.device_pb2.DeviceMessage.MessageType.LIGHT
        message.value = "set_on=" + str(user_input)
        message.id = int(self.user_input)

        try:
            self.client.client_socket.send(message.SerializeToString())
        except Exception as e:
            print(f"Error sending status message: {e}")

        self.update_table()
        self.popup.destroy()


if __name__ == "__main__":
    app = ClientGUI()
    app.mainloop()
