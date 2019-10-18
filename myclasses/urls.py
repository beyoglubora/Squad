from django.urls import path, re_path
from myclasses import views

urlpatterns = [
    path('', views.my_classes, name='dashboard'),
    re_path(r'^del[0-9]+', views.classDelete),
    path('classedit', views.edit_classes, name='edit_class_page')
]