import pika
import json
import os

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", 5672)

def send_mod_message(mod_data):
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST, RABBITMQ_PORT))
    channel = connection.channel()

    # Отправка в очередь mod_queue
    message = json.dumps(mod_data)
    channel.basic_publish(
        exchange='',
        routing_key='mod_queue',
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,  # Сообщение будет сохраняться
        )
    )
    print(f"Sent mod data to RabbitMQ: {mod_data}")
    connection.close()
