import socket


class IoTDevice:
    def __init__(self, device_id):
        self.device_id = device_id
        self.data = 0

    def connect(self):
        self.device_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.device_socket.connect((self.host, self.port))
            print(f"Connected to {self.host}:{self.port}")
        except Exception as e:
            print(f"Error: {e}")

    def send_data(self):
        try:
            while True:
                data = self.device_socket.recv(
                    1024
                )  # Receive data from the server (gateway)
                if not data:
                    break
                print(f"Received data: {data.decode()}")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.device_socket.close()

    def generate_data(self):
        # Emulate data generation
        self.data += 1
        return f"Device {self.device_id} - Data: {self.data}"


if __name__ == "__main__":
    device = IoTDevice(1)
    device.connect()
    device.send_data()
