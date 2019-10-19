from django.urls import path
from . import views

urlpatterns = [
    path('', views.display_groups),
    path('group_detail', views.group_detail, name="group_detail")
]