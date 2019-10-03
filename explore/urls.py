from django.urls import path

from . import views


urlpatterns = [
    path('', views.explore_page, name='explore'),
    path('create', views.create_class, name='create_class')
]