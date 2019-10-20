from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.display_groups),
    re_path(r'[0-9]+', views.group_detail),
    re_path('join-group', views.join_group),
    re_path('invite', views.invite)
]