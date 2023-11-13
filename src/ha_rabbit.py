import socket
import threading
import os
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
        try:
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

            return channel
        except pika.exceptions.AMQPError as amqp_error:
            print(f"Error creating RabbitMQ channel: {amqp_error}")
            raise

    def start(self):
        print(f'Listening to RabbitMQ on Port 5672')
        try:
            self.__channel.start_consuming()
        except KeyboardInterrupt:
            pass
        except pika.exceptions.AMQPError as amqp_error:
            print(f"Error starting RabbitMQ consumer: {amqp_error}")

class IoTGateway:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.devices = {}
        self.clients = {}
        self.input_threads = []
        self.device_id = 0
        self.client_id = 0
        self.running = True
        self.rabbitmq_exchanges = set()

        # Initialize RabbitMQ consumer
        self.rabbitmq_consumer = RabbitmqConsumer(self.handle_rabbitmq_message)
        self.rabbitmq_thread = threading.Thread(target=self.rabbitmq_consumer.start)
        self.rabbitmq_thread.daemon = True
        self.rabbitmq_thread.start()

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"Gateway is listening on {self.host}:{self.port}\n")

        user_command_thread = threading.Thread(target=self.handle_user_commands)
        user_command_thread.daemon = True
        user_command_thread.start()

        try:
            while self.running:
                client_socket, client_address = server_socket.accept()
                print(f"Accepted connection from {client_address}")
                client_thread = threading.Thread(target=self.handle_device, args=(client_socket,))
                client_thread.start()
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"Error in gateway: {e}")
        finally:
            server_socket.close()

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
            try:
                message = json.loads(data.decode())
            except json.JSONDecodeError as json_error:
                print(f"Invalid JSON message from client: {json_error}")
                return

            if "type" not in message:
                print("Invalid message from client. Missing 'type' field.")
                return

            if message["type"] == "UPDATE":
                update_message = {
                    "type": "UPDATE",
                    "value": json.dumps({key: {"type": value["type"]} for key, value in self.devices.items()})
                }
                print(f"\nDevice List: {json.dumps(update_message['value'], indent=2)}")
                try:
                    client_socket.send(json.dumps(update_message).encode())
                except Exception as e:
                    print(f"Error sending update message to client: {e}")
            else:
                try:
                    self.devices[message["id"]]["socket"].send(data)
                except KeyError:
                    print(f"Device with ID {message['id']} not found.")
                except Exception as e:
                    print(f"Error sending message to device: {e}")

        else:
            self.broadcast_clients(data)

    def handle_rabbitmq_message(self, ch, method, properties, body):
        try:
            print(f"\nReceived RabbitMQ message: {body.decode()}")
            self.broadcast_clients(body.decode())
        except Exception as e:
            print(f"Error handling RabbitMQ message: {e}")

    def broadcast_clients(self, data):
        for client_id, client in self.clients.items():
            try:
                client["socket"].send(data)
            except Exception as e:
                print(f"Error sending message to client: {e}")

    def handle_user_commands(self):
        while self.running:
            try:
                user_input = input("\nEnter a command (or 'quit' to exit): ")
                if user_input.lower() == "quit":
                    print("\nClosing the gateway...")
                    self.running = False
                    for device_id, device_info in self.devices.items():
                        try:
                            device_info["socket"].close()
                        except Exception as e:
                            print(f"Error closing device socket: {e}")
                    os._exit(1)

                elif user_input.lower() == "status":
                    self.broadcast_data()

                elif user_input.lower() == "help":
                    commands = {
                        "\nstatus": "Check the current status of the program.",
                        "quit": "Exit the program.",
                        "help": "Display a list of available commands.",
                        "add_exchange": "Add a RabbitMQ exchange.",
                        "remove_exchange": "Remove a RabbitMQ exchange.",
                        "list_exchanges": "List RabbitMQ exchanges.",
                        "select_sensors": "Select sensors via RabbitMQ.",
                    }
                    print("\nThese are the available commands:")
                    for command, desc in commands.items():
                        print(f"{command}: {desc}")

                elif user_input.lower() == "update":
                    device = input("Input the device ID: ")
                    self.send_message(int(device))

                elif user_input.lower() == "show":
                    print(self.devices)

                elif user_input.lower() == "add_exchange":
                    exchange_name = input("Enter the RabbitMQ exchange name to add: ")
                    self.rabbitmq_exchanges.add(exchange_name)
                    print(f"Added RabbitMQ exchange: {exchange_name}")

                elif user_input.lower() == "remove_exchange":
                    exchange_name = input("Enter the RabbitMQ exchange name to remove: ")
                    if exchange_name in self.rabbitmq_exchanges:
                        self.rabbitmq_exchanges.remove(exchange_name)
                        print(f"Removed RabbitMQ exchange: {exchange_name}")
                    else:
                        print(f"Exchange not found: {exchange_name}")

                elif user_input.lower() == "list_exchanges":
                    print("\nRabbitMQ Exchanges:")
                    for exchange in self.rabbitmq_exchanges:
                        print(exchange)

                elif user_input.lower() == "select_sensors":
                    self.select_sensors_via_rabbitmq()

                else:
                    print("Invalid command. Type help for all commands")
            except Exception as e:
                print(f"Error handling user command: {e}")

    def select_sensors_via_rabbitmq(self):
        try:
            if not self.rabbitmq_exchanges:
                print("No RabbitMQ exchanges added. Add exchanges before selecting sensors.")
                return

            print("\nSelecting sensors via RabbitMQ:")
            print("Available RabbitMQ Exchanges:")
            for idx, exchange in enumerate(self.rabbitmq_exchanges, 1):
                print(f"{idx}. {exchange}")

            selected_exchange_idx = int(input("Enter the index of the exchange to select sensors: ")) - 1
            selected_exchange = list(self.rabbitmq_exchanges)[selected_exchange_idx]

            print(f"Selected RabbitMQ Exchange: {selected_exchange}")
            print("Listening for sensor information. Type 'exit' to stop listening.\n")

            def callback(ch, method, properties, body):
                try:
                    decoded_body = body.decode()
                    print(f"Received RabbitMQ message: {decoded_body}")
                    self.broadcast_clients(decoded_body)
                except Exception as e:
                    print(f"Error handling RabbitMQ message: {e}")

            def input_thread():
                while True:
                    user_input = input()
                    if user_input.lower() == "exit":
                        print("\nStopping RabbitMQ consumer.")
                        try:
                            channel.stop_consuming()
                            connection.close()
                        except Exception as e:
                            print(f"Error stopping RabbitMQ consumer: {e}")
                        break

            connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672))
            channel = connection.channel()
            channel.exchange_declare(exchange=selected_exchange, exchange_type='fanout')

            result = channel.queue_declare(queue='', exclusive=True)
            queue_name = result.method.queue
            channel.queue_bind(exchange=selected_exchange, queue=queue_name)
            channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

            # Inicie uma nova thread para lidar com a entrada do usuário
            input_thread_instance = threading.Thread(target=input_thread)
            input_thread_instance.daemon = True
            input_thread_instance.start()

            # Adicione a thread de entrada à lista
            self.input_threads.append(input_thread_instance)

            try:
                channel.start_consuming()
            except KeyboardInterrupt:
                print("\nStopping RabbitMQ consumer.")
                try:
                    channel.stop_consuming()
                    connection.close()
                except Exception as e:
                    print(f"Error stopping RabbitMQ consumer: {e}")

        except Exception as e:
            print(f"Error selecting sensors via RabbitMQ: {e}")

if __name__ == "__main__":
    gateway = IoTGateway("localhost", 8080)
    gateway.start()
