import datetime
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify


class User(AbstractUser):
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=14, unique=True, null=True, blank=True)
    addresse = models.CharField(max_length=100, null=True, blank=True)
    watchlist = models.ManyToManyField('api.Variant', blank=True, related_name='interested_users')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        ordering = ['email']

    def save(self, *args, **kwargs):
        # Vérifie si l'email est déjà utilisé
        if User.objects.filter(email=self.email).exclude(pk=self.pk).exists():
            raise ValidationError("This email address already exists.")
        super().save(*args, **kwargs)

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
    brand = models.ForeignKey('api.Brand', blank=True, null=True, on_delete=models.SET_NULL, related_name="products")

    def __str__(self):
        return self.product_name


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
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
    logo = models.ImageField(upload_to='brands-logos/')
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
    url = models.ImageField(upload_to='variants-images/')
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name='images')
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.variant} - {self.color}"


class Order(models.Model):
    shipping_address = models.OneToOneField('api.ShippingAdress', on_delete=models.CASCADE, related_name='order')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    time_stamp = models.DateTimeField(default=timezone.now)

    def calculate_total(self):
        # Calculer le total des articles de commande liés à cette commande
        total = sum(item.total_price for item in self.order_items.all())
        self.total_amount = total

    def __str__(self):
        return f"Order {self.id} by {self.user.username} - Total: {self.total_amount} €"


class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    time_stamp = models.DateTimeField(default=timezone.now)
    payment_method = models.CharField(max_length=50, blank=False, null=False)
    currency = models.CharField(max_length=10, blank=False, null=False)
    transaction_id = models.CharField(max_length=250, blank=False, null=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        # Validation du montant du paiement
        if self.amount != self.order.total_amount:
            raise ValidationError("Le montant du paiement doit correspondre au montant total de la commande.")
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name='order_items')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')

    def save(self, *args, **kwargs):
        # Calculate total price before save
        self.total_price = self.unit_price * Decimal(self.quantity)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.variant} at {self.unit_price} € each, total: {self.total_price} €"


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')


class ShippingAdress(models.Model):
    receiver_first_name = models.CharField(max_length=100, blank=False, null=False)
    receiver_last_name = models.CharField(max_length=100, blank=False, null=False)
    country = models.CharField(max_length=100, blank=False, null=False)
    city = models.CharField(max_length=100, blank=False, null=False)
    address = models.CharField(max_length=100, blank=False, null=False)
    phone_number = models.CharField(max_length=20, blank=False, null=False)
    email = models.EmailField()


class Promo(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, null=True, blank=True)

    discount_type = models.CharField(max_length=20, choices=[
        ('percentage', 'percentage'),
        ('fixed', 'Fixed Amount'),
    ])
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def clean(self):
        # ensure only one field between category, variant and product is filled
        count = sum(bool(field) for field in [self.variant, self.category, self.product])
        if count != 1:
            raise ValidationError("Only one of 'variant', 'category', or 'product' must be set.")

    def __str__(self):
        if self.variant:
            return f"Promo for {self.variant} - {self.discount_value} {self.discount_type}"
        elif self.category:
            return f"Promo for {self.category} - {self.discount_value} {self.discount_type}"
        elif self.product:
            return f"Promo for {self.product} - {self.discount_value} {self.discount_type}"


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=10, choices=[('percentage', 'Pourcentage'), ('fixed', 'Fixe')])
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    usage_limit = models.IntegerField()
    used_count = models.IntegerField()
    expiry_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def is_valid(self):
        # Check if the coupon is still valid
        return self.is_active and (self.expiry_date is None or timezone.now() < self.expiry_date)