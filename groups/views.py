from django.shortcuts import render
from data import models as DataModel
from django.http import HttpResponseRedirect, JsonResponse
import re


def class_details(request, message=None, class_id=None):
    # The class_id should be retrieved from the sent request displaying the class_temp detail page.
    invalid = False
    if class_id is None:
        class_id = request.get_full_path().split('/')[-1]
        class_instance = DataModel.Class.objects.filter(class_id=class_id)
        if len(class_instance) == 0:
            invalid = True
            render(request, 'class_details.html', {'invalid': invalid})

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
        group = DataModel.Group.objects.filter(group_id=group_id).first()
        students = DataModel.Relationship.objects.filter(group_id=group_id)
        student_names = []
        for student in students:
            student_names.append(student.student_instance.first_name + " " + student.student_instance.last_name)
        active_groups[group] = ", ".join(student_names)

    groups = DataModel.Group.objects.filter(class_instance=class_id)
    active_groups = {}
    for group in groups:
        students = DataModel.Relationship.objects.filter(group_id=group.group_id)
        student_names = []
        for student in students:
            student_names.append(student.student_instance.first_name + " " + student.student_instance.last_name)
        active_groups[group] = ", ".join(student_names)
    student_relations = DataModel.Relationship.objects.filter(class_instance=class_id)
    in_group = False
    student_descriptions_skills = {}
    own_group = None
    relation = DataModel.Relationship.objects.filter(student_instance=request.user, class_instance=c)
    if len(relation) != 0:
        g_id = relation.first().group_id
        if g_id != -1:
            in_group = True
            g_instance = DataModel.Group.objects.filter(group_id=g_id).first()
            own_group = g_instance

    for student in student_relations:
        d = {}
        d['description'] = DataModel.Description.objects.filter(student_instance=student.student_instance, class_instance=c).first().description
        d['skills'] = DataModel.Skill_label.objects.filter(student_instance=student.student_instance, class_instance=c).first().label.split(";")
        d['skills'] = ", ".join(d['skills'])
        group = DataModel.Group.objects.filter(group_id=student.group_id).first()
        if group:
            d['group'] = group
        if in_group:
            pending = DataModel.Notification.objects.filter(sender_instance=request.user, receiver_instance=student.student_instance, class_instance=c, status=-1, group_instance=g_instance)
            if len(pending) > 0:
                d['pending'] = True
            else:
                d['pending'] = False
            if student.group_id == g_id:
                d['accepted'] = True
            else:
                d['accepted'] = False
        student_descriptions_skills[student] = d

    return render(request, 'class_details.html', {'class': c, 'groups': active_groups, 'enrolled': enrolled, 'invalid': invalid,
                                                  'student_descriptions_skills': student_descriptions_skills, "in_group": in_group,
                                                  "own_group": own_group})


def group_detail(request):
    invalid = False
    group_id = request.get_full_path().split('/')[-1]
    group = DataModel.Group.objects.filter(group_id=group_id)
    if len(group) == 0:
        invalid = True
        return render(request, 'group_detail.html', {'invalid': invalid})
    group = group.first()
    group_name = group.group_name
    group_members = dict()
    group_member_relations = DataModel.Relationship.objects.filter(group_id=group_id)
    for relation in group_member_relations:
        group_members[relation.student_instance.account_id] = relation.student_instance.first_name + " " + relation.student_instance.last_name
    in_group = request.user.pk in group_members
    messages = list(get_group_message(group_id))
    messages.reverse()

    # Check if enrolled
    class_id = group.class_instance
    relationships_in_class = DataModel.Relationship.objects.filter(class_instance_id=class_id)
    students_in_class_pks = []
    for relationship in relationships_in_class:
        students_in_class_pks.append(relationship.student_instance.pk)
    enrolled = request.user.pk in students_in_class_pks

    has_group = True
    relationship = DataModel.Relationship.objects.filter(student_instance=request.user, class_instance=class_id)
    if len(relationship) > 0:
        relation = relationship.first()
        if relation.group_id == -1:
            has_group = False

    student_relations = DataModel.Relationship.objects.filter(group_id=group_id)
    class_instance = group.class_instance
    class_id = class_instance.class_id
    student_descriptions_skills = {}
    for student in student_relations:
        d = {}
        d['description'] = DataModel.Description.objects.filter(student_instance=student.student_instance, class_instance=class_id).first().description
        d['skills'] = DataModel.Skill_label.objects.filter(student_instance=student.student_instance, class_instance=class_id).first().label.split(";")
        d['skills'] = ", ".join(d['skills'])
        student_descriptions_skills[student] = d

    isInstructor = DataModel.Account.objects.filter(account_id=request.user.account_id).first().is_instructor

    return render(request, 'group_detail.html', {'group_id': group_id,
                                                 'group_name': group_name,
                                                 'group_members': group_members,
                                                 'in_group': in_group,
                                                 'messages': messages,
                                                 'invalid': invalid,
                                                 'enrolled': enrolled,
                                                 'student_descriptions_skills': student_descriptions_skills,
                                                 'class': class_instance,
                                                 'has_group': has_group,
                                                 'is_instructor': isInstructor})


def request_to_join_group(request):
    group_id = request.POST.get("group_id")
    relations = DataModel.Relationship.objects.filter(group_id=group_id)
    group_instance = DataModel.Group.objects.filter(group_id=group_id).first()
    for relation in relations:
        DataModel.Notification.objects.create(sender_instance=request.user, receiver_instance=relation.student_instance, class_instance=relation.class_instance, group_instance=group_instance, status=9)
    return JsonResponse({"message": "Successfully request to join group"})

def create_group(request):
    group_name = request.POST.get('group_name')
    class_id = request.POST.get('class_id')
    class_instance = DataModel.Class.objects.filter(class_id=class_id).first()
    group = DataModel.Group.objects.create(group_name=group_name, class_instance=class_instance)
    group.refresh_from_db()
    if request.user.pk != class_instance.instructor_instance.account_id:
        relation = DataModel.Relationship.objects.filter(class_instance=class_instance, student_instance=request.user).first()
        relation.group_id = group.group_id
        relation.save()
    return JsonResponse({"group_id": group.group_id})


def remove_student_from_group(request):
    group_id = request.POST.get("group_id")
    student_id = request.POST.get("student_id")
    relation = DataModel.Relationship.objects.filter(student_instance=student_id, group_id=group_id).first()
    DataModel.Notification.objects.create(sender_instance=request.user, receiver_instance=relation.student_instance, class_instance=relation.class_instance, status=6)
    relation.group_id = -1
    relation.save()
    return JsonResponse({"message": "student successfully removed from group"})


def enroll_students_view(request):
    class_id = request.get_full_path().split('/')[-1]
    class_instance = DataModel.Class.objects.filter(class_id=class_id).first()
    students = DataModel.Account.objects.values()
    students_in_class = DataModel.Relationship.objects.filter(class_instance=class_instance)
    class_member_ids = []
    for student in students_in_class:
        class_member_ids.append(student.student_instance.account_id)
    stud_list = []
    for student in students:
        if student['account_id'] not in class_member_ids and not student['is_instructor']:
            student_instance = DataModel.Account.objects.filter(account_id=student['account_id']).first()
            enroll_notification = DataModel.Notification.objects.filter(sender_instance=request.user, receiver_instance=student_instance, class_instance=class_instance, status=3).first()
            if enroll_notification:
                student['notified'] = True
            else:
                student['notified'] = False
            stud_list.append(student)

    return render(request, 'enroll_students.html', context={'students': stud_list, 'class': class_instance})


def enroll_student(request):
    class_id = request.POST.get("class_id")
    class_instance = DataModel.Class.objects.filter(class_id=class_id).first()
    student_id = request.POST.get("student_id")
    student_instance = DataModel.Account.objects.filter(account_id=student_id).first()
    DataModel.Notification.objects.create(class_instance=class_instance, sender_instance=request.user, receiver_instance=student_instance, status=3)
    return JsonResponse({"message": "student was successfully notified of enrollment"})


def enroll_students(request):
    file = request.FILES.get("file")
    contents = file.read().decode("UTF-8-sig").lower()

    class_id = request.POST.get("class_id")
    class_instance = DataModel.Class.objects.filter(class_id=class_id).first()
    first = True
    index = None
    error_str = ""
    for line in contents.splitlines():
        if first:
            line = line.replace(" ", "").lower()
            columns = line.split(",")
            if "email" in columns:
                index = columns.index("email")
            elif "e-mail" in columns:
                index = columns.index("e-mail")
            else:
                response = JsonResponse({"message": "There was no column for email. Please make sure there is exactly one column in the csv file for email."})
                response.status_code = 403
                return response
            first = False
        else:
            row = line.split(",")
            email = row[index]
            student_instance = DataModel.Account.objects.filter(email=email).first()
            if email != "":
                if not student_instance:
                    error_str += email + " is not registered with Squad. <br>\n\r"
                else:
                    relation = DataModel.Relationship.objects.filter(student_instance=student_instance, class_instance=class_instance)
                    if len(relation) != 0:
                        error_str += email + " is already enrolled in your class. <br>\n\r"
                    else:
                        notification = DataModel.Notification.objects.filter(sender_instance=request.user, receiver_instance=student_instance, status=3, class_instance=class_instance)
                        if notification:
                            error_str += email + " has already been notified and still needs to fill out their skills and description. <br>"
                        else:
                            DataModel.Notification.objects.create(sender_instance=request.user, receiver_instance=student_instance, status=3, class_instance=class_instance)
    return JsonResponse({"message": error_str})

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
    relations = DataModel.Relationship.objects.filter(group_id=group_id)
    group_instance = DataModel.Group.objects.filter(group_id=group_id).first()
    DataModel.Notification.objects.filter(sender_instance=request.user, class_instance=relation.class_instance, group_instance=group_instance).delete()
    if len(relations) == 0:
        group_instance.delete()
        return JsonResponse({"message": "deleted group"})
    return JsonResponse({"message": "successfully left group"})


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
    # push notifications to the invited people
    student_id = int(request.POST.get('student_id'))
    class_id = int(request.POST.get('class_id'))
    class_instance = DataModel.Class.objects.filter(class_id=class_id).first()
    student_instance = DataModel.Account.objects.filter(account_id=student_id).first()
    relationship = DataModel.Relationship.objects.filter(student_instance=request.user, class_instance=class_instance).first()
    group_instance = DataModel.Group.objects.filter(group_id=relationship.group_id).first()
    DataModel.Notification.objects.create(class_instance=class_instance, sender_instance=request.user, receiver_instance=student_instance, group_instance=group_instance, status=-1)
    return JsonResponse({"message": "Successfully invite student"})


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
    description = request.POST.get('description', None)
    skills = request.POST.getlist('skills[]', None)
    skills = ", ".join(skills)
    class_id = request.POST.get('class_id', None)
    class_instance = DataModel.Class.objects.filter(class_id=class_id).first()
    print(skills)
    DataModel.Skill_label.objects.create(student_instance=request.user, class_instance=class_instance,
                                         label=skills)
    DataModel.Description.objects.create(class_instance=class_instance, student_instance=request.user,
                                         description=description)
    enroll(class_instance, request.user)
    data={"message": "Successfully enrolled in class"}
    notification = DataModel.Notification.objects.filter(sender_instance=class_instance.instructor_instance, receiver_instance=request.user, class_instance=class_instance, status=3)
    if "from-notification" in request.POST or len(notification) != 0:
        DataModel.Notification.objects.filter(sender_instance=class_instance.instructor_instance, receiver_instance=request.user, class_instance=class_instance, status=3).delete()

    return JsonResponse(data)


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


def remove_student(request):
    class_id = request.POST.get("class_id")
    student_id = request.POST.get("student_id")
    class_instance = DataModel.Class.objects.filter(class_id=class_id).first()
    student_instance = DataModel.Account.objects.filter(account_id=student_id).first()
    DataModel.Relationship.objects.filter(class_instance=class_instance, student_instance=student_instance).delete()
    DataModel.Skill_label.objects.filter(class_instance=class_instance, student_instance=student_instance).delete()
    DataModel.Description.objects.filter(class_instance=class_instance, student_instance=student_instance).delete()
    DataModel.Notification.objects.filter(sender_instance=student_instance, class_instance=class_instance).delete()
    DataModel.Notification.objects.create(sender_instance=request.user, receiver_instance=student_instance, class_instance=class_instance, status=8)

    return JsonResponse({'res:':"student removed successfully"})


def remove_group(request):
    class_id = request.POST.get("class_id")
    group_id = request.POST.get("group_id")
    class_instance = DataModel.Class.objects.filter(class_id=class_id).first()
    students_in_group = DataModel.Relationship.objects.filter(class_instance=class_instance, group_id=group_id)
    for student in students_in_group:
        relationship = DataModel.Relationship.objects.filter(class_instance=class_instance, student_instance=student.student_instance).first()
        DataModel.Notification.objects.create(sender_instance=request.user, receiver_instance=student.student_instance,
                                              class_instance=class_instance, status=6)
        relationship.group_id = -1
        relationship.save()
    DataModel.Group.objects.filter(group_id=group_id).delete()
    return JsonResponse({'result':"group removed successfully"})


def add_students_to_group_view(request):
    group_id = request.get_full_path().split('/')[-1]
    group_instance = DataModel.Group.objects.filter(group_id=group_id).first()
    class_instance = group_instance.class_instance
    class_id = class_instance.class_id
    student_relations = DataModel.Relationship.objects.filter(class_instance=class_id)
    group_member_relations = DataModel.Relationship.objects.filter(group_id=group_id)
    group_member_ids = []
    for gm in group_member_relations:
        group_member_ids.append(gm.student_instance.account_id)
    student_descriptions_skills = {}
    for student in student_relations:
        if student.student_instance.account_id not in group_member_ids:
            d = {}
            d['description'] = DataModel.Description.objects.filter(student_instance=student.student_instance,
                                                                    class_instance=class_instance).first().description
            d['skills'] = DataModel.Skill_label.objects.filter(student_instance=student.student_instance,
                                                               class_instance=class_instance).first().label.split(";")
            d['skills'] = ", ".join(d['skills'])
            if student.group_id == -1:
                d['in_group'] = False
            else:
                d['in_group'] = True
                d['group'] = DataModel.Group.objects.filter(group_id=student.group_id).first()
            d['email'] = student.student_instance.email
            student_descriptions_skills[student] = d
    return render(request, 'add_students.html', context={'group': group_instance,
                                                         'student_descriptions_skills': student_descriptions_skills,
                                                         'class': class_instance})


def add_student_to_group(request):
    student_id = request.POST.get("student_id")
    group_id = request.POST.get("group_id")
    class_id = request.POST.get("class_id")
    student_instance = DataModel.Account.objects.filter(account_id=student_id).first()
    class_instance = DataModel.Class.objects.filter(class_id=class_id).first()
    relation = DataModel.Relationship.objects.filter(student_instance=student_instance, class_instance=class_instance).first()
    if relation.group_id != -1:
        group_instance = DataModel.Group.objects.filter(group_id=relation.group_id).first()
        DataModel.Notification.objects.filter(sender_instance=student_instance, class_instance=class_instance, group_instance=group_instance).delete()
        new_group_instance = DataModel.Group.objects.filter(group_id=group_id).first()
        DataModel.Notification.objects.create(sender_instance=request.user, receiver_instance=student_instance, class_instance=class_instance, group_instance=new_group_instance, status=5)
    else:
        new_group_instance = DataModel.Group.objects.filter(group_id=group_id).first()
        DataModel.Notification.objects.create(sender_instance=request.user, receiver_instance=student_instance,
                                              class_instance=class_instance, group_instance=new_group_instance,
                                              status=7)
    relation.group_id = group_id
    relation.save()
    return JsonResponse({"message": "student successfully added to group"})


def unenroll(request):
    class_id = request.get_full_path().split('/')[-1]
    class_instance = DataModel.Class.objects.filter(class_id=class_id).first()
    DataModel.Relationship.objects.filter(class_instance=class_instance).filter(student_instance=request.user).delete()
    DataModel.Skill_label.objects.filter(class_instance=class_instance).filter(student_instance=request.user).delete()
    DataModel.Description.objects.filter(class_instance=class_instance).filter(student_instance=request.user).delete()
    DataModel.Notification.objects.filter(sender_instance=request.user, class_instance=class_instance).delete()
    return HttpResponseRedirect('/groups/class/'+class_id)


def add_message(request):
    group_id = request.POST.get('group_id', False)
    return render(request, 'new_message.html', context={'group_id': group_id})


def add_msg_to_DB(request):
    sender_name = "[%s %s]:"%(DataModel.Account.objects.filter(account_id=request.user.account_id).first().first_name, DataModel.Account.objects.filter(account_id=request.user.account_id).first().last_name)

    group_id = int(request.POST.get('group_id', False))
    subject = request.POST.get('msg_subject', False)
    body = request.POST.get('msg_body', False)

    # Get class id from group id
    class_id = DataModel.Relationship.objects.filter(group_id=group_id).first().class_instance.class_id

    # Set status code as -5 to indicate it's a group message in the notification.
    STATUS_CODE = -5

    # Get receiver
    receivers_obj = DataModel.Relationship.objects.filter(group_id=group_id)
    for obj in receivers_obj:
        receiver_id = obj.student_instance.account_id
        if request.user.account_id != receiver_id:
            create_notification(class_id, request.user.account_id, receiver_id, False, STATUS_CODE, group_id=group_id)

    # Create new message
    message = DataModel.Messages()
    message.group_id_id = group_id
    message.subject = subject
    message.body = sender_name + body
    message.save()

    return HttpResponseRedirect(str(group_id))


def get_group_message(group_id):
    messages = DataModel.Messages.objects.filter(group_instance=group_id)
    return messages