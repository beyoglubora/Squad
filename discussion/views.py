from django.http import JsonResponse
from django.shortcuts import render
from data import models as DataModel
import collections


def show_messages(request):
    """
    Display group messages only for group members and instructors.
    """

    # group_instance: the group instance of the currently viewed page
    # group_id = request.get_full_path().split('/')[-1] # get group id
    group_id = 1 # hard code for testing
    group_instance = DataModel.Group.objects.filter(group_id=group_id).first()

    isInstructor = DataModel.Account.objects.filter(account_id=request.user.account_id).first().is_instructor
    isEnrolled = False
    group_relation = list(DataModel.Relationship.objects.filter(group_id=group_id))
    for r in group_relation:
        if r.student_instance.account_id == request.user.account_id:
            isEnrolled = True
            break
    requesterID = request.user.account_id

    # get messages
    messages = list(DataModel.Messages.objects.filter(group_instance=group_instance))
    parent_msgs = list(DataModel.Messages.objects.filter(group_instance=group_instance, parent=-5)) # get parent messages
    msg_dict = {} # msg_dict = {parent_msg: [children_msgs]}
    for parent_msg in parent_msgs:
        children_msg = []
        for m in messages:
            if parent_msg.message_id == m.parent: # classify the children node
                children_msg.append(m)
        msg_dict[parent_msg] = children_msg
    # sort the dict based on the key's datetime
    od_msg_dict = collections.OrderedDict(sorted(msg_dict.items(), key=lambda t: t[0].date, reverse=True))

    return render(request, 'discussion.html', {'is_enrolled': isEnrolled,
                                               'is_instructor': isInstructor,
                                               'group_instance': group_instance,
                                               'msg_dict': od_msg_dict,
                                               'requesterID': requesterID})


def create_post(request):
    # class post -> -5
    # group post -> group id
    group_id = request.POST.get("group_id")
    group_instance = DataModel.Group.objects.filter(group_id=group_id).first()
    class_instance = group_instance.class_instance
    creator = request.user
    body = request.POST.get("body")
    print(body)
    parent = request.POST.get("parent_id")
    create_post_db(group_instance, class_instance, creator, body, parent)

    return JsonResponse({"result": True})


def delete_post(request):
    # creator and instructor
    # create parent -> all gone
    target_id = request.POST.get("post_id")
    target_instance = DataModel.Messages.objects.filter(message_id=target_id)
    if len(target_instance) != 1:
        # error here due to Not found
        pass
    target_instance = target_instance.first()
    delete_post_db(target_instance)

    return JsonResponse({"result": True})


def edit_post(request):
    # only creator can edit
    new_body = request.POST.get("new_body")
    target_id = request.POST.get("post_id")
    target_instance = DataModel.Messages.objects.filter(message_id=target_id)
    if len(target_instance) != 1:
        # error here due to Not found
        pass
    target_instance = target_instance.first()
    if request.user != target_instance.creator:
        # Error here due to not the creator
        pass
    edit_post_db(target_instance, new_body)

    return JsonResponse({"result": True})


def create_post_db(group_instance, class_instance, creator, body, parent=-5):
    """
    create a new post to db
    :param group_instance:
    :param class_instance:
    :param creator:
    :param body:
    :param parent:
    :return:
    """
    new_post = DataModel.Messages()
    new_post.group_instance = group_instance
    new_post.class_instance = class_instance
    new_post.creator = creator
    new_post.body = body
    new_post.parent = parent
    new_post.save()


def edit_post_db(target_post:DataModel.Messages, new_body):
    """
    Edit a post in db
    :param target_post:
    :param new_body:
    :return:
    """
    target_post.body = new_body
    target_post.save()


def delete_post_db(target_post:DataModel.Messages):
    """
    Delete a post in db, also including children if needed
    :param target_post:
    :return:
    """
    if target_post.parent > 0:
        # it's not a parent post, just delete itself
        target_post.delete()
        return
    # it's a parent post
    parent_id = target_post.message_id
    children = DataModel.Messages.objects.filter(parent=parent_id)
    children.delete()
    target_post.delete()
    return


