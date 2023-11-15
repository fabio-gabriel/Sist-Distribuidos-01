import signal
import proto.device_pb2
import proto.device_pb2_grpc
import grpc
from concurrent import futures


class IoTDevice(proto.device_pb2_grpc.MessageBrokerServicer):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = None
        self.running = True  # Flag to control the main loop
        self.device_type = "airconditioner"
        self.status = {"temperature": 21}

        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        proto.device_pb2_grpc.add_MessageBrokerServicer_to_server(self, self.server)

    def handle_shutdown(self, signum, frame):
        print("Closing the client...")
        self.running = False
        if self.client_socket:
            self.client_socket.close()

    def connect(self):
        signal.signal(signal.SIGBREAK, self.handle_shutdown)
        try:
            self.server.add_insecure_port("localhost:50051")
            print("here we go")
            self.server.start()
            self.server.wait_for_termination()

        except Exception as e:
            print(f"Error: {e}")

    def SendDeviceMessage(self, request, context):
        print("TA AQUI O REQUEST CARAI", request, context)
        if request.type == proto.device_pb2.DeviceMessage.MessageType.UPDATE:
            return proto.device_pb2.SendDeviceMessage(value=self.device_type)
        else:
            command, value = request.value.split("=")
            self.status = int(value)
            return super().SendDeviceMessage(value=self.status)


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
