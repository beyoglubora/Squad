from django.http import JsonResponse
from django.shortcuts import render
from data import models as DataModel


def show_messages(request):
    return render(request, 'discussion.html')


def create_post(request):
    # class post -> -5
    # group post -> group id

    return JsonResponse({"result": True})


def delete_post(request):
    # creator and instructor
    # create parent -> all gone

    return JsonResponse({"result": True})


def edit_post(request):
    # only creator can edit
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


