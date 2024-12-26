# В файле auth_service/rabbitmq.py

import json
import pika
import os

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", 5672)

# Переменные для канала и соединения
connection = None
channel = None

def create_rabbitmq_channel():
    global connection, channel
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST, RABBITMQ_PORT))
    channel = connection.channel()
    # Обязательно создаем очередь, если она еще не существует
    channel.queue_declare(queue="user_queue", durable=True)
    return channel

def get_rabbitmq_channel():
    if channel is None:
        create_rabbitmq_channel()
    return channel

def close_connection():
    global connection, channel
    if channel:
        channel.close()  # Закрываем канал
    if connection:
        connection.close()  # Закрываем соединение

# Эта функция отправляет сообщение в очередь RabbitMQ
def send_user_message(channel, user_data):
    message = json.dumps({"user_data": user_data})
    channel.basic_publish(
        exchange='',
        routing_key='user_queue',
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,  # Сообщение будет сохраняться в случае сбоя
        )
    )
    print("Sent user data to RabbitMQ")
