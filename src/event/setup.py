import pika

from src.core.config import rabbit_mq


def setup_queue():
    connection = pika.BlockingConnection(pika.URLParameters(rabbit_mq.build_connection()))
    channel = connection.channel()
    channel.queue_declare(queue="dispatch_messages", durable=True)
    connection.close()
