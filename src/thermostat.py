import socket
import signal
import threading
import time
import proto.device_pb2


class IoTDevice:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = None
        self.running = True  # Flag to control the main loop
        self.status = {"temperature": 21}

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

            periodic_updates_thread = threading.Thread(target=self.periodic_updates)
            periodic_updates_thread.daemon = True
            periodic_updates_thread.start()
        except Exception as e:
            print(f"Error: {e}")

    def send_data(self):
        message = proto.device_pb2.ThermostatStatus()
        message.temperature = self.status["temperature"]

        try:
            self.client_socket.send(message.SerializeToString())
        except Exception as e:
            print(f"Error sending status message: {e}")

    def periodic_updates(self):
        while self.running:
            self.send_data()
            time.sleep(5)  # Send status every 30 seconds


if __name__ == "__main__":
    client = IoTDevice("localhost", 8080)
    client.connect()

    while client.running:
        user_input = input("Enter data to send to the gateway (or 'quit' to exit): ")
        if user_input.lower() == "quit":
            print("Closing the client...")
            client.client_socket.close()
            break

    client.running = False  # Set the running flag to False to exit the receive_data loop
