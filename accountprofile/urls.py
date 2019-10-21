from django.urls import path, re_path
from accountprofile import views

urlpatterns = [
    path('', views.listRequestedmine),
    path('edit', views.changProfile, name='profedit'),
    re_path(r'[0-9]+', views.listRequested)
]