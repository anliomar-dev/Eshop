import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify


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


class Category(models.Model):
    category_name = models.CharField(max_length=150, null=False, blank=False)
    slug = models.SlugField(max_length=50, unique=True, blank=True, db_index=True)
    products = models.ManyToManyField('api.Product', related_name='categories')

    def save(self, *args, **kwargs):
        if not self.slug:  # Génère le slug seulement s'il n'est pas déjà défini
            base_slug = slugify(self.category_name)
            slug = base_slug
            count = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.category_name


class Product(models.Model):
    product_name = models.CharField(max_length=100, blank=False, null=False, unique=True)
    brand = models.ForeignKey('api.Brand', blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.product_name


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} - {self.product.product_name} - {self.rating}/5"


class Brand(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False)
    logo = models.ImageField(upload_to='logos/')
    slug = models.SlugField(max_length=50, unique=True, blank=True, db_index=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            count = 1
            while Brand.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Variant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    variant_name = models.CharField(max_length=50, null=True, blank=True)
    size = models.CharField(max_length=50, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    stock = models.IntegerField()

    def __str__(self):
        return f"{self.product.product_name} - {self.variant_name} - {self.size} - {self.price} - {self.stock} en stock"


class Color(models.Model):  # Héritage de models.Model
    color_name = models.CharField(max_length=30, null=True, blank=True)
    hex_code = models.CharField(max_length=20, null=False, blank=False)
    variants = models.ManyToManyField(Variant, related_name='colors')

    def __str__(self):
        return self.color_name


class Image(models.Model):  # Héritage de models.Model
    url = models.ImageField(upload_to='images/')
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name='images')
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.variant} - {self.color}"


"""
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


class Coupon:
    pass


class Promo:
    pass
"""