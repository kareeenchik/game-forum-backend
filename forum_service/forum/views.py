import requests
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Topic, Post, Category
from .serializers import TopicSerializer, PostSerializer, CategorySerializer

def send_to_audit(action, details, user_id):
    # Если user_id не пришел, ставим 0 или "Unknown", чтобы база не ругалась на пустой ID
    uid = user_id if user_id else 0
    try:
        # Используем алиас 'stats' без подчеркиваний
        url = "http://stats:8000/api/v1/logs/create/"
        payload = {
            "action": action,
            "details": details,
            "user_id": uid
        }
        requests.post(url, json=payload, timeout=1)
    except Exception as e:
        print(f"Ошибка логирования: {e}")

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        user_role = request.headers.get('X-User-Role')
        user_id = request.headers.get('X-User-Id')
        
        if not user_role or str(user_role).lower() != 'admin':
            return Response(
                {"detail": "Доступ запрещен: требуется роль администратора"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        response = super().create(request, *args, **kwargs)
        if response.status_code == 201:
            send_to_audit("CREATE_CATEGORY", f"Создана категория: {request.data.get('name')}", user_id)
        return response

class TopicViewSet(viewsets.ModelViewSet):
    queryset = Topic.objects.all().order_by('-created_at')
    serializer_class = TopicSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        user_id = self.request.headers.get('X-User-Id')
        instance = serializer.save()
        send_to_audit("CREATE_TOPIC", f"Создана тема: {instance.title}", user_id)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user_id = request.headers.get('X-User-Id')
        user_role = str(request.headers.get('X-User-Role', '')).lower()
        
        is_owner = user_id and str(instance.author_id) == str(user_id)
        is_admin = user_role == 'admin'

        if is_admin or is_owner:
            title = instance.title 
            self.perform_destroy(instance)
            send_to_audit("DELETE_TOPIC", f"Удалена тема: {title}", user_id)
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        return Response({"detail": "У вас нет прав на удаление этой темы!"}, 
                        status=status.HTTP_403_FORBIDDEN)

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        user_id = self.request.headers.get('X-User-Id')
        author_name = self.request.data.get('author_name', 'Аноним')
        instance = serializer.save(author_name=author_name)
        send_to_audit("CREATE_POST", f"Автор {author_name} оставил пост в теме ID: {instance.topic_id}", user_id)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user_id = request.headers.get('X-User-Id')
        user_role = str(request.headers.get('X-User-Role', '')).lower()

        is_admin = (user_role == 'admin')
        is_post_owner = user_id and str(instance.author_id) == str(user_id)
        is_topic_owner = user_id and str(instance.topic.author_id) == str(user_id)

        if is_admin or is_post_owner or is_topic_owner:
            post_id = instance.id
            author_log = instance.author_name
            self.perform_destroy(instance)
            send_to_audit("DELETE_POST", f"Удален комментарий ID: {post_id} (автор: {author_log})", user_id)
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        return Response({"detail": "Нет прав! Удалять может админ, автор поста или автор темы."}, 
                        status=status.HTTP_403_FORBIDDEN)