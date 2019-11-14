from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'class/[0-9]+', views.class_details),
    re_path(r'class/enroll/[0-9]+', views.enroll_form),
    re_path(r'class/unenroll/[0-9]+', views.unenroll),
    re_path(r'class/creategroup/[0-9]+', views.create_group),
    re_path(r'class/removestudent/', views.remove_student),
    re_path(r'class/removegroup/', views.remove_group),
    re_path(r'edit_group_name/[0-9]+', views.edit_group_name, name='edit-group-name'),
    re_path(r'[0-9]+', views.group_detail),
    re_path('join-group', views.join_group, name='join-group'),
    re_path('leave-group', views.leave_group, name='leave-group'),
    re_path('invite', views.invite, name='invite'),
    re_path('add_message', views.add_message),
    re_path('add_msg_to_DB', views.add_msg_to_DB),
]
