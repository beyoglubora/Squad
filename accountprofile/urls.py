from django.urls import path, re_path
from accountprofile import views

urlpatterns = [
    path('', views.my_profile),
    path('edit', views.change_profile, name='profedit'),
    re_path(r'[0-9]+', views.other_profile)
]