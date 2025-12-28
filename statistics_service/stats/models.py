from django.db import models

# Для детального списка событий (чтобы админ видел КТО и ЧТО удалил)
class AuditEvent(models.Model):
    action = models.CharField(max_length=100)  # new_topic, delete_post и т.д.
    details = models.TextField()               # "Пользователь admin удалил тему 'Гайд'"
    timestamp = models.DateTimeField(auto_now_add=True)
    user_id = models.IntegerField(null=True)

    class Meta:
        ordering = ['-timestamp'] # Свежие события вверху

# Твоя текущая модель (оставляем для счетчиков, если они нужны в статистике)
class ForumAggregate(models.Model):
    metric_name = models.CharField(max_length=100, unique=True)
    value = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.metric_name}: {self.value}"