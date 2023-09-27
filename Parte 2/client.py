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
    client = IoTClient("localhost", 12345)
    client.connect()
    client.receive_data()
