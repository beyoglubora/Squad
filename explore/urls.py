from django.urls import path

from . import views


urlpatterns = [
    path('', views.Explore.as_view(), name='explore'),
]