import pika
import json
import os

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", 5672)

def create_rabbit_connection():
    """Создание соединения с RabbitMQ"""
    return pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST, RABBITMQ_PORT))

def send_mod_message(mod_data):
    """Отправка сообщения в RabbitMQ"""
    connection = create_rabbit_connection()
    channel = connection.channel()

    # Отправка в очередь mod_queue
    message = json.dumps(mod_data)
    channel.basic_publish(
        exchange='',
        routing_key='mod_queue',
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,  # Сообщение будет сохраняться в случае сбоя
        )
    )
    print("Sent data to RabbitMQ")
    connection.close()
