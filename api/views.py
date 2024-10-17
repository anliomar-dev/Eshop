from django.shortcuts import render
from .models import User
from .serializers import UserSerializer, UserCreateSerializer
from rest_framework.generics import ListAPIView, ListCreateAPIView


class UserListCreateAPIView(ListCreateAPIView):
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer  # Pour la création
        return UserSerializer
