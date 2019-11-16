from django.urls import path, re_path
from notification import views

urlpatterns = [
    path('', views.notification_requested, name='notification'),
    path('readall', views.read_all_notifications),
    re_path(r'read/', views.read_notification, name='globalread'),
    re_path(r'accept/', views.accept_notification),
    re_path(r'decline/', views.decline_notification),
    re_path(r'acceptjoinrequest/', views.accept_join_notification),
    re_path(r'declinejoinrequest/', views.decline_join_notification),
    path('error', views.show_error),
]