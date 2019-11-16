from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
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
    notification_id = request.POST.get("notification_id")
    temp_obj = data.models.Notification.objects.filter(notification_id=notification_id)
    if not temp_obj:
        print("ERROR: cant find the notification")
        return JsonResponse({"message": "cant find notification"})
    else:
        temp_obj[0].read = True
        temp_obj[0].save()
        return JsonResponse({"message": "notification successfully marked as read"})


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
    notification_id = request.POST.get("notification_id")
    temp_obj = data.models.Notification.objects.filter(notification_id=notification_id)
    if not temp_obj:
        print("ERROR: cant find the notification")
        return False
    notification_instance = temp_obj[0]
    flag_success, message, is_actionable = accept_invitation(current_account=get_current_account(request), notification_instance=notification_instance)
    if flag_success:
        data.models.Notification.objects.filter(notification_id=notification_id).delete()
        return JsonResponse({"group_id": notification_instance.group_instance.group_id})
    else:
        response = JsonResponse({"message": message})
        response.status_code = 403
        return response


def accept_join_notification(request):
    notification_id = request.POST.get("notification_id")
    temp_obj = data.models.Notification.objects.filter(notification_id=notification_id)
    if not temp_obj:
        print("ERROR: cant find the notification")
        return False
    notification_instance = temp_obj[0]
    flag_success, message, is_actionable = accept_request(current_account=get_current_account(request),
                                                             notification_instance=notification_instance)
    if flag_success:
        data.models.Notification.objects.filter(sender_instance=notification_instance.sender_instance, class_instance=notification_instance.class_instance, group_instance=notification_instance.group_instance, status=notification_instance.status).delete()
        relation = data.models.Relationship.objects.filter(student_instance=notification_instance.sender_instance).first()
        relation.group_id = notification_instance.group_instance.group_id
        relation.save()
        data.models.Notification.objects.create(sender_instance=notification_instance.receiver_instance, receiver_instance=notification_instance.sender_instance, class_instance=notification_instance.class_instance, group_instance=notification_instance.group_instance, status=10)
        return JsonResponse({"group_id": notification_instance.group_instance.group_id})
    else:
        response = JsonResponse({"message": message})
        response.status_code = 403
        return response


def decline_join_notification(request):
    notification_id = request.POST.get("notification_id")
    temp_obj = data.models.Notification.objects.filter(notification_id=notification_id)
    if not temp_obj:
        print("ERROR: cant find the notification")
        return False
    notification_instance = temp_obj[0]
    flag_success, message = decline_invitation(current_account=get_current_account(request),
                                               notification_instance=notification_instance)
    if flag_success:
        data.models.Notification.objects.filter(notification_id=notification_id).delete()
        return JsonResponse({"message": "Successfully declined notification"})


def decline_notification(request):
    """
        :param request:
        :return:
        """
    notification_id = request.POST.get("notification_id")
    temp_obj = data.models.Notification.objects.filter(notification_id=notification_id)
    if not temp_obj:
        print("ERROR: cant find the notification")
        return False
    notification_instance = temp_obj[0]
    flag_success, message = decline_invitation(current_account=get_current_account(request), notification_instance=notification_instance)
    if flag_success:
        messages.info(request, message)
        data.models.Notification.objects.filter(notification_id=notification_id).delete()
        return JsonResponse({"message": "Successfully declined notification"})


def show_error(request):
    return render(request, 'notification_error.html')