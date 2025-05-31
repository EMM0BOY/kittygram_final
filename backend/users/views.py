from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import permissions
from .models import User
from .serializers import CustomUserSerializer

class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = CustomUserSerializer