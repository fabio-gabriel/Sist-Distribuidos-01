import socket
import threading
import time
import signal


class IoTGateway:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = []
        self.running = True

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"Gateway is listening on {self.host}:{self.port}")

        while self.running:
            client_socket, client_address = server_socket.accept()
            print(f"Accepted connection from {client_address}")
            self.clients.append(client_socket)
            client_thread = threading.Thread(
                target=self.handle_client, args=(client_socket,)
            )
            client_thread.start()

    def handle_client(self, client_socket):
        try:
            while self.running:
                data = client_socket.recv(1024)
                if not data:
                    break
                print(f"Received message from client: {data.decode()}")

            self.clients.remove(client_socket)
            client_socket.close()
        except Exception as e:
            print(f"Error handling client: {e}")


if __name__ == "__main__":
    gateway = IoTGateway("localhost", 8080)
    gateway.start()
