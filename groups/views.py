from django.shortcuts import render
from data import models as DataModel
from django.http import HttpResponseRedirect
import re


def class_details(request, message=None, class_id=None):
    # The class_id should be retrieved from the sent request displaying the class_temp detail page.
    if class_id is None:
        class_id = request.get_full_path().split('/')[-1]
    group_relations = DataModel.Relationship.objects.filter(class_instance=class_id)
    c = DataModel.Class.objects.filter(class_id=class_id).first()
    # Get unique active group ids for a class_temp
    relationships_in_class = DataModel.Relationship.objects.filter(class_instance=c)
    students_in_class_pks = []
    for relationship in relationships_in_class:
        students_in_class_pks.append(relationship.student_instance.pk)
    enrolled = request.user.pk in students_in_class_pks
    print(enrolled)
    active_group_ids = set()
    for relation in group_relations:
        active_group_ids.add(relation.group_id)
    if -1 in active_group_ids:
        active_group_ids.remove(-1)  # remove the default group

    active_groups = dict()
    for group_id in active_group_ids:
        group_name = DataModel.Group.objects.filter(group_id=group_id)[0].group_name
        active_groups[group_id] = group_name

    # Get active students
    student_relations = DataModel.Relationship.objects.filter(class_instance=class_id, group_id=-1)
    active_students = set()
    for relation in student_relations:
        active_students.add(relation.student_instance.first_name + " " + relation.student_instance.last_name)
    return render(request, 'class_details.html', {'class': c, 'groups': active_groups, 'active_students': student_relations,
                                                  'enrolled': enrolled, 'message': message})


def group_detail(request):
    group_id = request.get_full_path().split('/')[-1]
    group_name = DataModel.Group.objects.filter(group_id=group_id)[0].group_name

    group_members = dict()
    group_member_relations = DataModel.Relationship.objects.filter(group_id=group_id)
    for relation in group_member_relations:
        group_members[relation.student_instance.account_id] = relation.student_instance.first_name + " " + relation.student_instance.last_name
    in_group = request.user.pk in group_members
    return render(request, 'group_detail.html', {'group_id': group_id,
                                                 'group_name': group_name,
                                                 'group_members': group_members,
                                                 'in_group': in_group})


def edit_group_name(request):
    group_id = request.get_full_path().split('/')[-1]
    group = DataModel.Group.objects.filter(group_id=group_id).first()
    if request.method == 'POST':
        group.group_name = request.POST['group-name']
        group.save()
        return HttpResponseRedirect("/groups/"+group_id)
    return render(request, 'edit_group_name.html', context={'group': group})


def leave_group(request):
    group_id = request.POST.get("group_id")
    relation = DataModel.Relationship.objects.filter(student_instance=request.user, group_id=group_id).first()
    relation.group_id = -1
    relation.save()
    class_id = relation.class_instance.class_id
    message = "Successfully left group"
    return class_details(request, message, class_id)


def join_group(request):
    group_id = request.POST.get("group_id")
    sender_id = request.user.pk
    relation = DataModel.Relationship.objects.filter(group_id=group_id).first()
    class_id = relation.class_instance.class_id
    # push notifications to other group members
    group_members = request.POST.get('group_members')
    receivers = re.findall(r'\d+(?=:)', group_members)
    for receiver in receivers:
        create_notification(1, sender_id, receiver, False, 3)

    message = "Successfully sent join notifications. Waiting for responses..."
    return class_details(request, message, class_id)


def invite(request):
    sender_id = request.user.pk
    # push notifications to the invited people
    invited_id = int(request.POST.get('invited_id'))
    class_id = int(request.POST.get('class_id'))
    create_notification(1, sender_id, invited_id, False, -1)
    message = "Successfully sent invite notifications. Waiting for responses..."
    return class_details(request, message, class_id)


def create_notification(class_id, sender, receiver, read, status):
    notification = DataModel.Notification()
    notification.class_instance_id = class_id
    notification.sender_instance_id = sender
    notification.receiver_instance_id = receiver
    notification.read = read
    notification.status = status
    notification.save()
    return


def enroll_form(request):
    class_id = request.get_full_path().split('/')[-1]
    class_instance = DataModel.Class.objects.filter(class_id=class_id).first()
    student_instance = request.user
    if request.method == "POST":
        enroll(class_instance, student_instance)
        DataModel.Description.objects.create(class_instance=class_instance, student_instance=student_instance,
                                             description=request.POST["description"])
        DataModel.Skill_label.objects.create(student_instance=student_instance, class_instance=class_instance,
                                             label=request.POST["skill_set"])
        return HttpResponseRedirect('/groups/class/' + class_id)
    return render(request, 'enroll_form.html', context={'class': class_instance})


def enroll(class_instance, student_instance):
    DataModel.Relationship.objects.create(class_instance=class_instance, student_instance=student_instance)


def unenroll(request):
    class_id = request.get_full_path().split('/')[-1]
    class_instance = DataModel.Class.objects.filter(class_id=class_id).first()
    DataModel.Relationship.objects.filter(class_instance=class_instance).filter(student_instance=request.user).delete()
    DataModel.Skill_label.objects.filter(class_instance=class_instance).filter(student_instance=request.user).delete()
    DataModel.Description.objects.filter(class_instance=class_instance).filter(student_instance=request.user).delete()
    return HttpResponseRedirect('/groups/class/'+class_id)

