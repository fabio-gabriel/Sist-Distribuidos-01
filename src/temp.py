import socket
import signal
import threading
import random
import time

class TemperatureSensor:
    def __init__(self, host, port, sensor_id):
        self.host = host
        self.port = port
        self.sensor_id = sensor_id
        self.client_socket = None
        self.running = True  # Flag to control the main loop

    def handle_shutdown(self, signum, frame):
        print("Closing the sensor...")
        self.running = False
        if self.client_socket:
            self.client_socket.close()

    def connect(self):
        signal.signal(signal.SIGINT, self.handle_shutdown)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((self.host, self.port))
            print(f"Connected to {self.host}:{self.port}")
            receive_thread = threading.Thread(target=self.receive_data)
            receive_thread.daemon = True
            receive_thread.start()
        except Exception as e:
            print(f"Error: {e}")

    def send_temperature_data(self, temperature):
        try:
            data = f"Sensor ID: {self.sensor_id}, Temperature: {temperature}"
            self.client_socket.send(data.encode())
        except Exception as e:
            print(f"Error sending data: {e}")

    def generate_temperature(self):
        while self.running:
            temperature = round(random.uniform(20.0, 30.0), 2)
            self.send_temperature_data(temperature)
            time.sleep(5)  # Simulate temperature updates every 5 seconds

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
    sensor = TemperatureSensor("localhost", 8080, "sensor001")
    sensor.connect()

    # Create a thread to generate and send temperature data
    temperature_thread = threading.Thread(target=sensor.generate_temperature)
    temperature_thread.daemon = True
    temperature_thread.start()

    while sensor.running:
        user_input = input("Enter 'quit' to exit the sensor: ")
        if user_input.lower() == "quit":
            print("Closing the sensor...")
            sensor.client_socket.close()
            break
