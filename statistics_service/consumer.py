import pika
import json
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from stats.models import ForumAggregate

def callback(ch, method, properties, body):
    data = json.loads(body)
    event_type = data.get('event')

    print(f" [x] Получено событие: {event_type}")

    if event_type == 'new_topic':
        stat, created = ForumAggregate.objects.get_or_create(metric_name='total_topics')
        stat.value += 1
        stat.save()
        print(f" [v] Счетчик тем обновлен! Текущее значение: {stat.value}")

    if event_type == 'new_post':
        print(f" [NOTIFY] Пользователю {data['author_id']} пришло уведомление о новом комментарии!")

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='forum_events')

print(' [*] Ожидание сообщений из Форума. Для выхода нажмите CTRL+C')

channel.basic_consume(queue='forum_events', on_message_callback=callback, auto_ack=True)
channel.start_consuming()
