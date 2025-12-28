import pika
import json
from django.db import models

def send_to_rabbit(event_type, data):

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
        print(f" [v] Событие '{event_type}' отправлено в очередь")
    except Exception as e:
        print(f" [!] Ошибка RabbitMQ: {e}")

class Category(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self): return self.name

class Topic(models.Model):
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    title = models.CharField(max_length=200)
    content = models.TextField(default="") 
    author_id = models.IntegerField()
    author_name = models.CharField(max_length=100, default="User") 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return self.title

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            send_to_rabbit('new_topic', {
                'id': self.id, 
                'title': self.title,
                'author_id': self.author_id,
                'author_name': self.author_name
            })
    def delete(self, *args, **kwargs):
        send_to_rabbit('delete_topic', {
            'id': self.id,
            'title': self.title,
            'author_id': self.author_id
        })
        super().delete(*args, **kwargs)

class Post(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='posts')
    parent = models.ForeignKey(
        'self', 
        null=True, 
        blank=True, 
        on_delete=models.CASCADE, 
        related_name='replies'
    ) 
    content = models.TextField()
    author_id = models.IntegerField()
    author_name = models.CharField(max_length=100, default="User")
    likes = models.IntegerField(default=0) 
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            send_to_rabbit('new_post', {
                'id': self.id, 
                'topic_id': self.topic.id,
                'author_id': self.author_id,
                'author_name': self.author_name
            })
    
    def delete(self, *args, **kwargs):
        send_to_rabbit('delete_post', {
            'id': self.id,
            'topic_id': self.topic.id,
            'author_id': self.author_id
        })
        super().delete(*args, **kwargs)