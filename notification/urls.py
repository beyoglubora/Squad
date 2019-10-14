from django.urls import path, re_path
from notification import views

urlpatterns = [
    path('', views.notification_requested),
    re_path(r'read/[0-9]+', views.read_nofitication, name='globalread'),
    re_path(r'accept/[0-9]+', views.accept_nofitication),
    re_path(r'decline/[0-9]+', views.decline_nofitication),
    path('error', views.show_error),
]