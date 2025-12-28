from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from django.contrib.auth import authenticate
from .serializers import UserRegistrationSerializer

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({"message": "User created"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    
    if user:
        return Response({
            "user_id": user.id,
            "username": user.username,
            "role": user.role,
            "nickname": user.nickname
        })
    return Response({"error": "Invalid credentials"}, status=400)