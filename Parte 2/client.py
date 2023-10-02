import socket


class IoTClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = None

    def connect(self):
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
            while True:
                data = self.client_socket.recv(
                    1024
                )  # Receive data from the server (gateway)
                if not data:
                    break
                print(f"Received data: {data.decode()}")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.client_socket.close()


if __name__ == "__main__":
    client = IoTClient("localhost", 8080)
    client.connect()

    try:
        while client.running:
            user_input = input(
                "Enter data to send to the gateway (or 'quit' to exit): "
            )
            if user_input.lower() == "quit":
                break
            client.send_data(user_input)
    except KeyboardInterrupt:
        pass  # Handle Ctrl+C gracefully

    client.running = False
