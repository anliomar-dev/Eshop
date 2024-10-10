from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=14, unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    addresse = models.CharField(max_length=100, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class Product:
    pass


class Order:
    pass


class OrderItem:
    pass


class Cart:
    pass


class ShippingAdress:
    pass


class Payment:
    pass


class Review:
    pass


class Coupon:
    pass


class Promo:
    pass


class Category:
    pass


class Color:
    pass


class Image:
    pass


class Brand:
    pass


class Variant:
    pass

