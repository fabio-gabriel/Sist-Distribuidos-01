import time
import random
import pika
import json
from typing import Dict

class RabbitmqPressurePublisher:
    def __init__(self) -> None:
        self.__host = "localhost"
        self.__port = 5672
        self.__username = "guest"
        self.__password = "guest"
        self.__exchange = "pressure_exchange"
        self.__routing_key = ""
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
        channel.exchange_declare(exchange=self.__exchange, exchange_type='fanout')
        return channel

    def send_pressure_data(self, pressure: float):
        message_body = {"pressure": pressure}
        self.send_message(message_body)

    def send_message(self, body: Dict):
        message = json.dumps(body)
        self.__channel.basic_publish(
            exchange=self.__exchange,
            routing_key=self.__routing_key,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2
            )
        )

if __name__ == "__main__":
    rabbitmq_pressure_publisher = RabbitmqPressurePublisher()

    try:
        while True:
            pressure = random.uniform(980.0, 1050.0)
            pressure_format = "{:.2f}".format(pressure)
            rabbitmq_pressure_publisher.send_pressure_data(pressure_format)

            print(f"Pressure: {pressure}")
            time.sleep(5)
    except KeyboardInterrupt:
        print("Pressure Sensor: Closing...")
