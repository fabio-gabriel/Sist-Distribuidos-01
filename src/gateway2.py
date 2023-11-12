import socket
import threading
import os
import proto.device_pb2
import json
import pika

class RabbitmqConsumer:
    def __init__(self, callback) -> None:
        self.__host = "localhost"
        self.__port = 5672
        self.__username = "guest"
        self.__password = "guest"
        self.__queue = "data_queue"
        self.__callback = callback
        self.__channel = self.__create_channel()

    def __create_channel(self):
        connection_parameters = pika.ConnectionParameters(
            host=self.__host,
            port=self.__port,
            credentials=pika.PlainCredentials(
                username=self.__username,
                password=self.__password
            )
        )

        channel = pika.BlockingConnection(connection_parameters).channel()
        channel.queue_declare(
            queue=self.__queue,
            durable=True
        )
        channel.basic_consume(
            queue=self.__queue,
            auto_ack=True,
            on_message_callback=self.__callback
        )

        return channel

    def start_consuming_thread(self):
        print(f'Listen Rabbitmq on Port 5672')
        threading.Thread(target=self.__channel.start_consuming).start()

def minha_callback(ch, method, properties, body):
    print(body)

rabbitmq_consumer = RabbitmqConsumer(minha_callback)
rabbitmq_consumer.start_consuming_thread()

class IoTGateway:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.devices = {}
        self.clients = {}
        self.device_id = 0
        self.client_id = 0
        self.running = True

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"Gateway is listening on {self.host}:{self.port}")

        user_command_thread = threading.Thread(target=self.handle_user_commands)
        user_command_thread.daemon = True
        user_command_thread.start()

        while self.running:
            client_socket, client_address = server_socket.accept()
            print(f"Accepted connection from {client_address}")
            client_thread = threading.Thread(target=self.handle_device, args=(client_socket,))
            client_thread.start()

    def handle_device(self, client_socket):
        try:
            device_type = client_socket.recv(1024).decode()

            if device_type == "client":
                client_id = self.client_id
                self.client_id += 1
                self.clients[client_id] = {"socket": client_socket}
                print(f"Assigned Client ID {client_id} to client {client_socket.getpeername()}")

            else:
                device_id = self.device_id
                self.device_id += 1
                self.devices[device_id] = {"socket": client_socket, "type": device_type}
                print(f"Assigned Device ID {device_id} to client {client_socket.getpeername()} of type {device_type}")

            while self.running:
                data = client_socket.recv(1024)
                if not data:
                    break
                self.handle_messages(data, device_type, client_socket)

            del self.devices[device_id]
            client_socket.close()
        except Exception as e:
            print(f"Error handling client: {e}")

    def handle_messages(self, data, device_type, client_socket):
        if device_type == "client":
            message = proto.device_pb2.DeviceMessage()
            message.ParseFromString(data)

            if message.type == proto.device_pb2.DeviceMessage.MessageType.UPDATE:
                update_message = proto.device_pb2.DeviceMessage()
                update_message.type = proto.device_pb2.DeviceMessage.MessageType.UPDATE

                device_list = {key: {"type": value["type"]} for key, value in self.devices.items()}
                print(device_list)
                update_message.value = json.dumps(device_list)

                client_socket.send(update_message.SerializeToString())
            else:
                self.devices[message.id]["socket"].send(data)

        else:
            self.broadcast_clients(data)

    def send_message(self, device_id):
        if device_id in self.devices:
            device_info = self.devices[device_id]
            device_socket, device_type = device_info["socket"], device_info["type"]

            if device_type == "airconditioner":
                temperature = input("Type in the air conditioner temperature: ")

                message = proto.device_pb2.DeviceMessage()
                message.type = proto.device_pb2.DeviceMessage.MessageType.AC
                message.value = "set_temperature=" + temperature

                try:
                    device_socket.send(message.SerializeToString())
                except Exception as e:
                    print(f"Error sending status message: {e}")

            elif device_type == "lightbulb":
                switch = input("Switch on/off the lightbulb? (1 for on, 0 for off): ")

                message = proto.device_pb2.DeviceMessage()
                message.type = proto.device_pb2.DeviceMessage.MessageType.LIGHT
                message.value = "set_on=" + switch

                try:
                    device_socket.send(message.SerializeToString())
                except Exception as e:
                    print(f"Error sending status message: {e}")

        else:
            print("Did not find in", self.devices)

    def broadcast_data(self):
        for device_id, device in self.devices.items():
            device_socket = device["socket"]
            device_type = device["type"]
            try:
                if device_type == "airconditioner":
                    message = proto.device_pb2.DeviceMessage()
                    message.type = proto.device_pb2.DeviceMessage.MessageType.AC
                    message.value = "get_temperature"

                elif device_type == "lightbulb":
                    message = proto.device_pb2.DeviceMessage()
                    message.type = proto.device_pb2.DeviceMessage.MessageType.LIGHT
                    message.value = "get_on"

                    wrapper = proto.device_pb2.LightbulbMessage()
                    wrapper.status.CopyFrom(message)

                device_socket.send(wrapper.SerializeToString())

            except Exception as e:
                print(f"Error sending message to device {device_id}: {e}")

    def broadcast_clients(self, data):
        for client_id, client in self.clients.items():
            client["socket"].send(data)

    def handle_user_commands(self):
        while self.running:
            user_input = input("Enter a command (or 'quit' to exit): ")
            if user_input.lower() == "quit":
                print("Closing the gateway...")
                self.running = False
                for device_id, device_info in self.devices.items():
                    device_info["socket"].close()
                os._exit(1)

            elif user_input.lower() == "status":
                self.broadcast_data()

            elif user_input.lower() == "help":
                commands = {
                    "\nstatus": "Check the current status of the program.",
                    "quit": "Exit the program.",
                    "help": "Display a list of available commands.\n",
                }
                print("\nThese are the available commands:")
                for command, desc in commands.items():
                    print(f"{command}: {desc}")

            elif user_input.lower() == "update":
                device = input("Input the device ID: ")
                self.send_message(int(device))

            elif user_input.lower() == "show":
                print(self.devices)

            else:
                print("Invalid command. Type help for all commands")

if __name__ == "__main__":
    gateway = IoTGateway("localhost", 8080)
    gateway_thread = threading.Thread(target=gateway.start)
    gateway_thread.start()

    rabbitmq_consumer_thread = threading.Thread(target=rabbitmq_consumer.start)
    rabbitmq_consumer_thread.start()

    # Wait for threads to finish
    gateway_thread.join()
    rabbitmq_consumer_thread.join()
