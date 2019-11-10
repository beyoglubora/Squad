from django.urls import path, re_path
from notification import views

urlpatterns = [
    path('', views.notification_requested, name='notification'),
    path('readall', views.read_all_notifications),
    re_path(r'read/[0-9]+', views.read_notification, name='globalread'),
    re_path(r'accept/[0-9]+', views.accept_notification),
    re_path(r'decline/[0-9]+', views.decline_notification),
    path('error', views.show_error),
]