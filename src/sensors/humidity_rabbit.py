import time
import random
import pika
import json
from typing import Dict

class RabbitmqPublisher:
    def __init__(self) -> None:
        self.__host = "localhost"
        self.__port = 5672
        self.__username = "guest"
        self.__password = "guest"
        self.__exchange = "humidity_exchange"
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

    def send_humidity_data(self, humidity: float):
        message_body = {"humidity": humidity}
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
    rabbitmq_publisher = RabbitmqPublisher()

    try:
        while True:
            humidity = random.uniform(30.0, 70.0)
            rabbitmq_publisher.send_humidity_data(humidity)
            print(f"{humidity}%")
            time.sleep(5)
    except KeyboardInterrupt:
        print("Humidity Sensor: Closing...")
