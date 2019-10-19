from django.shortcuts import render
from data import models as DataModel

# Create your views here.

def display_groups(request):

    # class_id = request.class_id
    class_id = 1


    # Filter all unique existing groups for class_id
    same_class_relationship = DataModel.Relationship.objects.filter(class_instance=class_id)

    group_ids = set()
    for relationship in same_class_relationship:
        group_ids.add(relationship.group_id)

    groups = dict()
    for group_id in group_ids:
        group_name = DataModel.Group.objects.filter(group_id=group_id)[0].group_name
        groups[group_id] = group_name

    return render(request, 'groups.html', {'groups': groups})


def group_detail(request):
    return render(request, 'group_detail.html')
