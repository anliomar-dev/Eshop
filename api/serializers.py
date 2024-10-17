from django.db import models
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  # Champ uniquement pour l'entrée

    class Meta:
        model = User
        fields = ['username', 'email', 'password']  # Inclut le mot de passe

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])  # Hachage du mot de passe
        user.save()
        return user