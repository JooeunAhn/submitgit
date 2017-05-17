import pika
import json

from submitgit.settings.loader import load_credential


def connect_queue(data):
    credential = pika.PlainCredentials(load_credential('RQ_ID'),
                                       load_credential('RQ_PASSWORD'))
    parameters = pika.ConnectionParameters(load_credential('RQ_IP'),
                                           5672,
                                           "/",
                                           credential)
    connection = pika.BlockingConnection(parameters=parameters)
    channel = connection.channel()

    channel.queue_declare(queue=load_credential('QUEUE_NAME'), durable=True)
    message = json.dumps(data)
    channel.basic_publish(exchange='',
                          routing_key=load_credential('QUEUE_NAME'),
                          body=message,
                          properties=pika.BasicProperties(
                              delivery_mode=2,
                          ))
    connection.close()
