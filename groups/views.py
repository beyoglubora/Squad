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
    messages = get_group_message(group_id)
    return render(request, 'group_detail.html', {'group_id': group_id,
                                                 'group_name': group_name,
                                                 'group_members': group_members,
                                                 'in_group': in_group,
                                                 'messages': messages})


def edit_group_name(request):
    group_id = request.get_full_path().split('/')[-1]
    group = DataModel.Group.objects.filter(group_id=group_id).first()
    invalid = False
    if request.method == 'POST':
        if len(request.POST['group-name']) < 20:
            group.group_name = request.POST['group-name']
            group.save()
            return HttpResponseRedirect("/groups/"+group_id)
        else:
            invalid = True
    return render(request, 'edit_group_name.html', context={'group': group, 'invalid': invalid})


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
    create_notification(class_id, sender_id, invited_id, False, -1)
    message = "Successfully sent invite notifications. Waiting for responses..."
    return class_details(request, message, class_id)


def create_notification(class_id, sender, receiver, read, status, group_id=None):
    notification = DataModel.Notification()
    notification.class_instance_id = class_id
    notification.sender_instance_id = sender
    notification.receiver_instance_id = receiver
    notification.read = read
    notification.status = status
    if group_id:
        notification.group_instance_id = group_id
    if check_notification(notification):
        notification.save()
    return


def check_notification(notification):
    invites = DataModel.Notification.objects.filter(class_instance_id=notification.class_instance_id,
                                                    sender_instance=notification.sender_instance,
                                                    receiver_instance=notification.receiver_instance,
                                                    status=-1)
    # if not notification.group_instance_id and not invites:
    if not invites:
        return True
    return False


def enroll_form(request):
    class_id = request.get_full_path().split('/')[-1]
    class_instance = DataModel.Class.objects.filter(class_id=class_id).first()
    student_instance = request.user
    invalid = False
    if request.method == "POST":
        skill_set = ""
        for key in request.POST:
            if "skill_set" in key:
                skill_set += request.POST[key] + ";"
        skill_set = skill_set[:-1]
        description = request.POST["description"]
        if check_enroll(skill_set, description):
            enroll(class_instance, student_instance)
            DataModel.Skill_label.objects.create(student_instance=student_instance, class_instance=class_instance,
                                                 label=skill_set)
            DataModel.Description.objects.create(class_instance=class_instance, student_instance=student_instance,
                                                 description=description)
            return HttpResponseRedirect('/groups/class/' + class_id)
        else:
            invalid = True

    return render(request, 'enroll_form.html', context={'class': class_instance, 'invalid': invalid})


def check_enroll(skill_set, description):
    if len(description) == 0 or len(description) > 100:
        return False
    skills = skill_set.split(';')
    if skills == ['']:
        return False
    for skill in skills:
        if not skill or len(skill) > 20 or ";" in skill:
            return False
    return True


def enroll(class_instance, student_instance):
    DataModel.Relationship.objects.create(class_instance=class_instance, student_instance=student_instance)


def unenroll(request):
    class_id = request.get_full_path().split('/')[-1]
    class_instance = DataModel.Class.objects.filter(class_id=class_id).first()
    DataModel.Relationship.objects.filter(class_instance=class_instance).filter(student_instance=request.user).delete()
    DataModel.Skill_label.objects.filter(class_instance=class_instance).filter(student_instance=request.user).delete()
    DataModel.Description.objects.filter(class_instance=class_instance).filter(student_instance=request.user).delete()
    return HttpResponseRedirect('/groups/class/'+class_id)

def add_message(request):
    group_id = request.POST.get('group_id', False)
    return render(request, 'new_message.html', context={'group_id': group_id})

def add_msg_to_DB(request):
    group_id = int(request.POST.get('group_id', False))
    subject = request.POST.get('msg_subject', False)
    body = request.POST.get('msg_body', False)

    # create_notification(class_id, sender, receiver, read, status, group_id=None)

    # Get class id from group id
    class_id = DataModel.Relationship.objects.filter(group_id=group_id).first().class_instance.class_id

    # Set status code as -5 to indicate it's a group message in the notification.
    STATUS_CODE = -5

    # Get receiver
    receivers_obj = DataModel.Relationship.objects.filter(group_id=group_id)
    for obj in receivers_obj:
        receiver_id = obj.student_instance.account_id
        create_notification(class_id, request.user.account_id, receiver_id, False, STATUS_CODE, group_id=group_id)

    # Create new message
    message = DataModel.Messages()
    message.group_id_id = group_id
    message.subject = subject
    message.body = body
    message.save()

    return render(request, 'new_message.html')


def get_group_message(group_id):
    messages = DataModel.Messages.objects.filter(group_id=group_id)
    return messages