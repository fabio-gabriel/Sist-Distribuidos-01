import socket
import signal


class IoTDevice:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = None
        self.running = True  # Flag to control the main loop

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
        except Exception as e:
            print(f"Error: {e}")

    def send_data(self, data):
        try:
            self.client_socket.send(data.encode())
        except Exception as e:
            print(f"Error sending data: {e}")

    def receive_data(self):
        try:
            while self.running:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                print(f"Received data: {data.decode()}")

            self.client_socket.close()
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    client = IoTDevice("localhost", 8080)
    client.connect()

    while client.running:
        user_input = input("Enter data to send to the gateway (or 'quit' to exit): ")
        if user_input.lower() == "quit":
            print("Closing the client...")
            client.client_socket.close()
            break
        client.send_data(user_input)

    client.running = (
        False  # Set the running flag to False to exit the receive_data loop
    )
