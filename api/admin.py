from django.contrib import admin
from django.contrib.admin import AdminSite
from .models import User, Product, Category, Variant, Color, Image
from django.urls import reverse, path
# Register your models here.


class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email']
    filter_horizontal = ('user_permissions', 'groups',)


admin.site.register(User, UserAdmin)

