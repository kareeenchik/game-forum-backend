from rest_framework import serializers
from .models import Category, Topic, Post

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'topic', 'content', 'author_id', 'author_name', 'created_at']

class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        # ДОБАВИЛИ 'category' В СПИСОК
        fields = ['id', 'title', 'content', 'author_id', 'author_name', 'created_at', 'category']