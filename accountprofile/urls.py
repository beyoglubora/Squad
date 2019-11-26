from django.urls import path, re_path
from accountprofile import views

urlpatterns = [
    re_path(r'editprofile/', views.edit_profile),
    re_path(r'editclass/', views.edit_class),
    re_path(r'deleteclass/', views.delete_class),
    re_path(r'editenroll/', views.edit_enroll),
    re_path(r'[0-9]+', views.listRequested),
]