from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'[0-9]+', views.show_messages),
    re_path(r'create/', views.create_post),
    re_path(r'delete/', views.delete_post)
]