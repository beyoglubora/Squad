from django.shortcuts import render
from data import models as DataModel
import re


def display_groups(request):

    # The class_id should be retrieved from the sent request displaying the class detail page.
    class_id = 1

    group_relations = DataModel.Relationship.objects.filter(class_instance=class_id)

    # Get unique active group ids for a class
    active_group_ids = set()
    for relation in group_relations:
        active_group_ids.add(relation.group_id)
    active_group_ids.remove(-1) # remove the default group

    active_groups = dict()
    for group_id in active_group_ids:
        group_name = DataModel.Group.objects.filter(group_id=group_id)[0].group_name
        active_groups[group_id] = group_name

    # Get active students
    student_relations = DataModel.Relationship.objects.filter(class_instance=class_id, group_id=-1)
    active_students = set()
    for relation in student_relations:
        active_students.add(relation.student_instance.first_name + " " + relation.student_instance.last_name)

    return render(request, 'groups.html', {'groups': active_groups, 'active_students': student_relations})


def group_detail(request):
    group_id = request.get_full_path().split('/')[-1]

    group_name = DataModel.Group.objects.filter(group_id=group_id)[0].group_name

    group_members = dict()
    group_member_relations = DataModel.Relationship.objects.filter(group_id=group_id)
    for relation in group_member_relations:
        group_members[relation.student_instance.account_id] = relation.student_instance.first_name + " " + relation.student_instance.last_name
    return render(request, 'group_detail.html', {'group_id': group_id, 'group_name': group_name, 'group_members': group_members})
