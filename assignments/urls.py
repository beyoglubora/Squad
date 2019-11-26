from django.urls import path
from django.conf.urls import url

from . import views


urlpatterns = [
    path('instructor/<int:class_pk>', views.assignment_main_page, name='instructor_assign'),
    path('detail/<int:a_pk>', views.show_assignment_detail, name='instructor_detail'),
    path('student/upload/group/<int:g_pk>/assignment/<int:a_pk>', views.show_student_upload),
    path('group/<int:group_pk>', views.show_assignment_group, name='group_assignment_detail'),
    path('removeassignment/', views.remove_assignment, name='remove-assignment')
]
