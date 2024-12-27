import pika
import json
import os

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", 5672)

def create_channel():
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST, RABBITMQ_PORT))
    channel = connection.channel()
    channel.queue_declare(queue='user_queue', durable=True)
    channel.queue_declare(queue='mod_queue', durable=True)
    return connection, channel

rabbitmq_connection, rabbitmq_channel = create_channel()

def consume_user_data():
    def callback(ch, method, properties, body):
        user_data = json.loads(body)
        print(f"Received user data: {user_data}")


    rabbitmq_channel.basic_consume(queue='user_queue', on_message_callback=callback, auto_ack=True)
    rabbitmq_channel.start_consuming()

def consume_mod_data():
    def callback(ch, method, properties, body):
        mod_data = json.loads(body)
        print(f"Received mod data: {mod_data}")


    rabbitmq_channel.basic_consume(queue='mod_queue', on_message_callback=callback, auto_ack=True)
    rabbitmq_channel.start_consuming()