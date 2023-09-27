import socket
import threading
import sys
import time


class IoTDevice:
    def __init__(self, device_id):
        self.device_id = device_id
        self.data = 0

    def generate_data(self):
        # Emulate data generation
        self.data += 1
        return f"Device {self.device_id} - Data: {self.data}"


class IotGateway:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.devices = [IoTDevice(device_id) for device_id in range(1, 4)]

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"Gateway is listening on {self.host}:{self.port}")

        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Accepted connection from {client_address}")
            client_thread = threading.Thread(
                target=self.handle_client, args=(client_socket,)
            )
            client_thread.start()

    def handle_client(self, client_socket):
        try:
            while True:
                # Send data from devices to the client
                for device in self.devices:
                    data = device.generate_data()
                    client_socket.send(data.encode())

                time.sleep(5)  # Sleep for 5 seconds before sending data again

        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()


if __name__ == "__main__":
    gateway = IotGateway("localhost", 12345)
    gateway.start()
