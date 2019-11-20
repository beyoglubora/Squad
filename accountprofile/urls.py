from django.urls import path, re_path
from accountprofile import views

urlpatterns = [
    path('edit', views.changProfile, name='profedit'),
    re_path(r'editclass/', views.edit_class),
    re_path(r'deleteclass/', views.delete_class),
    re_path(r'editenroll/', views.edit_enroll),
    re_path(r'[0-9]+', views.listRequested),
]