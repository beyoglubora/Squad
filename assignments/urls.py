from django.urls import path
from django.conf.urls import url

from . import views


urlpatterns = [
    path('', views.assignment_main_page),
    path('upload', views.show),
    path('student/upload', views.show_student_upload)
]
