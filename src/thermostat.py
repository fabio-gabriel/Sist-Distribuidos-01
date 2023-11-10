import socket
import signal
import threading
import time
import random
import proto.device_pb2


class IoTDevice:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = None
        self.running = True  # Flag to control the main loop
        self.device_type = "thermostat"  # Device type (thermostat)
        self.status = {"temperature": 21}  # Initial state with temperature

    def handle_shutdown(self, signum, frame):
        # Function to handle client shutdown
        print("Closing the client...")
        self.running = False  # Set the running flag to False
        if self.client_socket:
            self.client_socket.close()  # Close the client socket

    def connect(self):
        signal.signal(signal.SIGBREAK, self.handle_shutdown)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((self.host, self.port))
            print(f"Connected to {self.host}:{self.port}")
            self.send_device_type()  # Send the device type as part of the handshake

            periodic_updates_thread = threading.Thread(target=self.periodic_updates)
            periodic_updates_thread.daemon = True
            periodic_updates_thread.start()  # Start a thread for periodic updates
        except Exception as e:
            print(f"Error: {e}")

    def send_device_type(self):
        try:
            # Send the device type as part of the handshake
            self.client_socket.send(self.device_type.encode())
        except Exception as e:
            print(f"Error sending device type: {e}")

    def send_data(self):
        message = proto.device_pb2.DeviceMessage()
        message.type = proto.device_pb2.DeviceMessage.MessageType.THERMOSTAT
        message.value = str(self.status["temperature"])

        try:
            self.client_socket.send(message.SerializeToString())
        except Exception as e:
            print(f"Error sending status message: {e}")

    def periodic_updates(self):
        while self.running:
            # Set a random temperature
            self.status["temperature"] = random.randint(18, 31)

            self.send_data()  # Send the temperature data to the server
            time.sleep(5)  # Send status every 5 seconds


if __name__ == "__main__":
    client = IoTDevice("localhost", 8080)
    client.connect()  # Establish the connection with the server

    while client.running:
        user_input = input("Enter data to send to the gateway (or 'quit' to exit): ")
        if user_input.lower() == "quit":
            print("Closing the client...")
            client.client_socket.close()  # Close the client socket
            break

    client.running = False  # Set the running flag to False to exit the receive_data loop
