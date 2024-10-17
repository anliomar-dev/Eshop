from .views import UserListCreateAPIView
from django.urls import path

urlpatterns = [
    path('users', UserListCreateAPIView.as_view(), name="all_users"),

]