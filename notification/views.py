from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import messages

# Create your views here.
from .functions import *
import data.models
# assume that I get a account_instance from Bora
'''
stu2 = data.models.Account.objects.all()[1]
stu3 = data.models.Account.objects.all()[2]
stu4 = data.models.Account.objects.all()[3]
notification1 = data.models.Notification.objects.all()[0]
notification2 = data.models.Notification.objects.all()[1]
notification3 = data.models.Notification.objects.all()[2]
'''


def get_current_account(request):
    """
    get current account()
    :return:
    """
    return request.user


def notification_requested(request):
    """
    :param request:
    :return: render with list_notifications
    """
    return render(request, 'student_notification.html',
                  {'list_notification': account_get_notification(get_current_account(request)),
                   'current_user': get_current_account(request)})


def read_notification(request):
    """
    :param request:
    :return: False or HttpResponseRedirect('/notification')
    """
    temp_str = request.get_full_path()
    notification_id = temp_str.split("read/")[-1]
    temp_obj = data.models.Notification.objects.filter(notification_id=notification_id)
    if not temp_obj:
        print("ERROR: cant find the notification")
        return HttpResponseRedirect('/notification')
    else:
        temp_obj[0].read = True
        temp_obj[0].save()
        return HttpResponseRedirect('/notification')


def read_all_notifications(request):
    """
    Read all
    :param request:
    :return:
    """
    read_all(get_current_account(request))
    return HttpResponseRedirect('/notification')



def accept_notification(request):
    """
    :param request:
    :return:
    """
    temp_str = request.get_full_path()
    notification_id = temp_str.split("accept/")[-1]
    temp_obj = data.models.Notification.objects.filter(notification_id=notification_id)
    if not temp_obj:
        print("ERROR: cant find the notification")
        return False
    notification_instance = temp_obj[0]
    flag_success, message = accept_invitation(current_account=get_current_account(request), notification_instance=notification_instance)
    if flag_success:
        return render(request, 'student_notification.html',
                      {'message': message})
    else:
        return render(request, 'student_notification.html',
                      {'message': message})


def decline_notification(request):
    """
        :param request:
        :return:
        """
    temp_str = request.get_full_path()
    notification_id = temp_str.split("decline/")[-1]
    temp_obj = data.models.Notification.objects.filter(notification_id=notification_id)
    if not temp_obj:
        print("ERROR: cant find the notification")
        return False
    notification_instance = temp_obj[0]
    flag_success, message = decline_invitation(current_account=get_current_account(request), notification_instance=notification_instance)
    if flag_success:
        messages.info(request, message)
        return HttpResponseRedirect('/notification')
    else:
        return render(request, 'student_notification.html',
                      {'message': message})


def show_error(request):
    return render(request, 'notification_error.html')