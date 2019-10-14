from django.urls import path, re_path
from myclasses import views

urlpatterns = [
    path('', views.listRequested, name='dashboard'),
    re_path(r'^del[0-9]+', views.classDelete)
]