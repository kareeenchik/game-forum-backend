from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('moderator', 'Moderator'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    nickname = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.username} - {self.role}"