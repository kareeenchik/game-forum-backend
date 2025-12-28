import pika
import json

def send_event(event_type, data):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        channel.queue_declare(queue='forum_events')


        message = {
            'event': event_type,
            'data': data
        }

        channel.basic_publish(
            exchange='',
            routing_key='forum_events',
            body=json.dumps(message)
        )
        connection.close()
    except Exception as e:
        print(f"Ошибка при отправке в RabbitMQ: {e}")