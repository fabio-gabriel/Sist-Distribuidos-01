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
        self.device_type = "airconditioner"
        self.status = {"isOn": False, "temperature": 21}

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

    def send_data(self, type):
        if type == "status":
            message = proto.device_pb2.StatusMessage()
            message.is_on = self.status["isOn"]
            message.temperature = self.status["temperature"]

        else:
            if self.status["isOn"]:
                temp = input("Type in the desired temperature: ")
                message = proto.device_pb2.ActionMessage()
                message.action = proto.device_pb2.ActionMessage.TEMPERATURE
                message.value = str(temp)

                wrapper = proto.device_pb2.AirConditionerMessage()
                wrapper.action.CopyFrom(message)
            else:
                on = input("The air conditioner is off. Turn it on? (type 'yes' or 'no'): ")
                if on == "no":
                    return
                message = proto.device_pb2.ActionMessage()
                message.action = proto.device_pb2.ActionMessage.STATUS
                message.value = str(1)

                wrapper = proto.device_pb2.AirConditionerMessage()
                wrapper.action.CopyFrom(message)
        try:
            self.client_socket.send(wrapper.SerializeToString())
        except Exception as e:
            print(f"Error sending status message: {e}")

    def receive_data(self):
        try:
            while self.running:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                action_message = proto.device_pb2.ActionMessage()
                action_message.ParseFromString(data)

                if action_message.action == proto.device_pb2.ActionMessage.STATUS:
                    self.status["isOn"] = action_message.value == "on"
                elif action_message.action == proto.device_pb2.ActionMessage.TEMPERATURE:
                    self.status["temperature"] = int(action_message.value)
                print("The device has been updated: ", self.status)
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
        elif user_input.lower() == "status":
            print(client.status)
        client.send_data(user_input)

    client.running = False  # Set the running flag to False to exit the receive_data loop
