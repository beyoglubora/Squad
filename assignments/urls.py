from django.urls import path
from django.conf.urls import url

from . import views


urlpatterns = [
    path('instructor/<int:class_pk>', views.assignment_main_page, name='instructor_assign'),
    path('upload', views.show),
    path('student/upload', views.show_student_upload)
]
