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
    return temp_notification_objects


def is_all_read(account_instance):
    # account_instance is an object of data.models.Account
    temp_notification_objects = data.models.Notification.objects.filter(receiver_instance=account_instance)\
        .filter(read=False)
    if not temp_notification_objects:
        return True
    else:
        return False


'''
    assume that Notification. status is enum
    -2: instructor deleting you  notification
    -1: invitation pending
    1: invitation accepted
    2: invitation declined
    3: others
'''


def decline_invitation(current_account: data.models.Account, notification_instance: data.models.Notification):
    sender = notification_instance.sender_instance
    receiver = notification_instance.receiver_instance
    status = notification_instance.status
    if current_account != receiver:
        print("you're processing others notification, strange here")
        return False
    if status != -1:
        print("notification has been processed, strange here")
        return False
    notification_instance.status = 2
    notification_instance.read = True
    notification_instance.save()
    # maybe you need to notify sender
    return sender


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
    new_group = data.models.Group(group_id=group_id)
    new_group.save()


def accept_invitation(current_account: data.models.Account, notification_instance: data.models.Notification):
    sender = notification_instance.sender_instance
    receiver = notification_instance.receiver_instance
    temp_class = notification_instance.class_instance
    status = notification_instance.status
    if current_account != receiver:
        print("you're processing others notification, strange here")
        return False
    if status != -1:
        print("notification has been processed, strange here")
        return False
    if receiver.is_instructor:
        print("invitation from an instructor, strange here")
        return False
    # check if sender still in class
    sender_in_class = is_in_class(sender, temp_class)
    if not sender_in_class:
        print("sender not in class")
        notification_instance.status = 3
        notification_instance.save()
        return False
    # check if receiver still in class
    receiver_in_class = is_in_class(receiver, temp_class)
    if not receiver_in_class:
        print("receiver not in class")
        notification_instance.status = 3
        notification_instance.save()
        return False
    # check if receiver have a group in that class
    receiver_have_group = have_group_class(receiver, temp_class)
    if receiver_have_group:
        print("receiver already have a group in that class")
        return False
    sender_have_group = have_group_class(sender, temp_class)
    if sender_have_group:
        # if sender have a group
        group_num = sender_have_group
        join_group(receiver, temp_class, group_num)
        notification_instance.status = 1
        notification_instance.read = True
        notification_instance.save()
        return True
    else:
        # if sender don't have a group
        group_num = notification_instance.notification_id
        join_group(receiver, temp_class, group_num)
        join_group(sender, temp_class, group_num)
        add_group_name(group_num)
        notification_instance.status = 1
        notification_instance.read = True
        notification_instance.save()
        return True


if __name__ == '__main__':
    pass