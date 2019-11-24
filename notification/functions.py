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


def account_get_notification(account_instance):
    temp_notification_objects = data.models.Notification.objects.filter(receiver_instance=account_instance)
    return temp_notification_objects[::-1]


def is_all_read(account_instance):
    # account_instance is an object of data.models.Account
    temp_notification_objects = data.models.Notification.objects.filter(receiver_instance=account_instance)\
        .filter(read=False)
    if not temp_notification_objects:
        return True
    else:
        return False


def read_all(account_instance):
    """
    Read all notification
    :param account_instance:
    :return:
    """
    temp_notification_objects = data.models.Notification.objects.filter(receiver_instance=account_instance) \
        .filter(read=False)
    for notification_instance in temp_notification_objects:
        notification_instance.read = True
        notification_instance.save()


'''
    assume that Notification. status is enum
    -2: instructor deleting you  notification
    -1: invitation pending
    1: invitation accepted
    2: invitation declined
    
    -3: others
    -5: group message
    
    todo: 
    3:application pending/ 
    4:application/accepted 
    5:application/declined
'''


def decline_invitation(current_account, notification_instance):
    sender = notification_instance.sender_instance
    receiver = notification_instance.receiver_instance
    status = notification_instance.status
    notification_instance.read = True
    notification_instance.save()
    message = ''
    if current_account != receiver:
        print("you're processing others notification, strange here")
        message = "you're processing others notification, strange here"
        return False, message
    # maybe you need to notify sender
    message = "You declined it"
    return sender, message


def is_in_class(student_instance, class_instance):
    in_class = data.models.Relationship.objects.filter(student_instance=student_instance) \
        .filter(class_instance=class_instance)
    if not in_class:
        return False
    return True


def have_group_class(student_instance, class_instance):
    temp_obj = data.models.Relationship.objects.filter(student_instance=student_instance) \
        .filter(class_instance=class_instance)
    if not temp_obj:
        return False
    if temp_obj[0].group_id < 0:
        return False
    else:
        return temp_obj[0].group_id

def still_in_group_class(student_instance, class_instance, group_instance):
    temp_obj = data.models.Relationship.objects.filter(student_instance=student_instance) \
        .filter(class_instance=class_instance)
    if not temp_obj:
        return False
    if temp_obj[0].group_id < 0:
        return False
    if temp_obj[0].group_id != group_instance.group_id:
        return False
    else:
        return True


def join_group(student_instance, class_instance, group_id):
    temp_obj = data.models.Relationship.objects.filter(student_instance=student_instance) \
        .filter(class_instance=class_instance)
    if not temp_obj:
        # student not in that class
        return False
    if len(temp_obj) > 1:
        print("ERROR: something wrong in database!")
        return False
    if temp_obj[0].group_id > 0:
        # student already have a group in that class
        return False
    # join stu in group, just change group_id
    temp_obj[0].group_id = group_id
    temp_obj[0].save()
    return True


def add_group_name(group_id:int):
    temp_obj = data.models.Group.objects.filter(group_id=group_id)
    if temp_obj:
        # already have that group_id
        return False
    new_group = data.models.Group(group_id=group_id, group_name='Group'+str(group_id))
    new_group.save()


def accept_invitation(current_account, notification_instance):
    """
    Logic now:
    both have a group: error
    One has a group: let the other in
    Neither has a group: make a new group for them to let them in
    :param current_account:
    :param notification_instance:
    :return:
    """
    sender = notification_instance.sender_instance
    receiver = notification_instance.receiver_instance
    temp_class = notification_instance.class_instance
    status = notification_instance.status
    message = ''
    notification_instance.read = True
    group_id = notification_instance.group_instance.group_id
    group = data.models.Group.objects.filter(group_id=group_id)
    if len(group) == 0:
        print("group no longer exists")
        message = "You can no longer join this group because it does not exist any longer."
        return False, message, False
    group_instance = group.first()
    notification_instance.save()
    if current_account != receiver:
        print("you're processing others notification, strange here")
        message = "you're processing others notification, strange here"
        return False, message, False
    if status != -1 and status != 3:
        print("notification has been processed, strange here")
        message = "notification has been processed, strange here"
        return False, message, False
    # if sender.is_instructor:
    #     print("invitation from an instructor, strange here")
    #     message = "invitation from an instructor, strange here"
    #     return False, message
    # check if sender still in class
    sender_in_class = is_in_class(sender, temp_class)
    # check if receiver still in class
    receiver_in_class = is_in_class(receiver, temp_class)
    if not receiver_in_class:
        print("receiver not in class")
        message = "You can not join this group because you are no longer enrolled in this class. Please re-enroll if you would like to join this group."
        return False, message, True
    if not sender_in_class:
        print("sender not in class")
        message = "You can not join this group because the student that sent you this invitation is no longer in the class anymore. If you would still like to join this group, please request to join from their group page."
        notification_instance.status = -3
        notification_instance.save()
        return False, message, False
    # check if receiver have a group in that class
    receiver_have_group = have_group_class(receiver, temp_class)
    sender_have_group = have_group_class(sender, temp_class)
    sender_still_in_group = still_in_group_class(sender, temp_class, group_instance)
    if receiver_have_group:
        print("You have a group")
        message = "You can not join this group because you are already in a group for this class. Please leave your current group if you want to accept this invitation."
        return False, message, True
    if not sender_still_in_group:
        print("Sender has a group")
        message = "You can not join this group because the student that sent you this invitation is no longer in the group anymore. If you would still like to join this group, please request to join from their group page."
        return False, message, False
    else:
        # if sender have a group, receiver don't
        # receiver join sender's group
        group_num = sender_have_group
        join_group(receiver, temp_class, group_num)
        notification_instance.status = 1
        notification_instance.save()
        message = "You have successfully joined the group!"
        return True, message, False
    # elif receiver_have_group:
    #     # sender join receiver's group
    #     group_num = receiver_have_group
    #     join_group(sender, temp_class, group_num)
    #     notification_instance.status = 1
    #     notification_instance.save()
    #     message = "Sender joined your group"
    #     return True, message
    # else:
    #     # if both don't have a group
    #     # make a new group for them by the notification_id
    #     group_num = notification_instance.notification_id
    #     join_group(receiver, temp_class, group_num)
    #     join_group(sender, temp_class, group_num)
    #     add_group_name(group_num)
    #     notification_instance.status = 1
    #     notification_instance.save()
    #     message = "You made a new group now"
    #     return True, message

def accept_request(current_account, notification_instance):
    """
    Logic now:
    both have a group: error
    One has a group: let the other in
    Neither has a group: make a new group for them to let them in
    :param current_account:
    :param notification_instance:
    :return:
    """
    sender = notification_instance.sender_instance
    receiver = notification_instance.receiver_instance
    temp_class = notification_instance.class_instance
    status = notification_instance.status
    message = ''
    notification_instance.read = True
    group_id = notification_instance.group_instance.group_id
    group = data.models.Group.objects.filter(group_id=group_id)
    if len(group) == 0:
        print("group no longer exists")
        message = "You can no longer accept this request because this group does not exist anymore."
        data.models.Notification.objects.filter(notification_id=notification_instance.notification_id).delete()
        return False, message, False
    group_instance = group.first()
    notification_instance.save()
    if current_account != receiver:
        print("you're processing others notification, strange here")
        message = "you're processing others notification, strange here"
        return False, message, False
    # if sender.is_instructor:
    #     print("invitation from an instructor, strange here")
    #     message = "invitation from an instructor, strange here"
    #     return False, message
    # check if sender still in class
    sender_in_class = is_in_class(sender, temp_class)
    # check if receiver still in class
    receiver_in_class = is_in_class(receiver, temp_class)
    if not receiver_in_class:
        print("receiver not in class")
        message = "You can not accept this request because you are no longer enrolled in this class."
        data.models.Notification.objects.filter(notification_id=notification_instance.notification_id).delete()
        return False, message, True
    if not sender_in_class:
        print("sender not in class")
        message = "You can not accept this request because the student that sent you this request is no longer in the class anymore."
        notification_instance.status = -3
        notification_instance.save()
        data.models.Notification.objects.filter(notification_id=notification_instance.notification_id).delete()
        return False, message, False
    # check if receiver have a group in that class
    receiver_have_group = have_group_class(receiver, temp_class)
    sender_have_group = have_group_class(sender, temp_class)
    receiver_still_in_group = still_in_group_class(receiver, temp_class, group_instance)
    if not receiver_still_in_group:
        print("Sender has a group")
        message = "You can not accept this request because you are no longer in the group."
        data.models.Notification.objects.filter(notification_id=notification_instance.notification_id).delete()
        return False, message, False
    else:
        # if sender have a group, receiver don't
        # receiver join sender's group
        group_num = sender_have_group
        join_group(receiver, temp_class, group_num)
        # notification_instance.status = 1
        # notification_instance.save()
        message = "You have successfully joined the group!"
        return True, message, False


if __name__ == '__main__':
    pass