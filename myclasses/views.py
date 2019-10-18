from django.http import HttpResponseRedirect
from django.shortcuts import render
from data import models as DataModel


def getIDInstance():
    """
    :return: current student instance who clicked
    """
    return DataModel.Account.objects.all()[2]


def get_my_created_classes(instructor):
    classes = DataModel.Class.objects.filter(instructor=instructor)
    return classes


def get_enrolled_classes(student):
    """
    :param student: student_instance
    :return: a list of classes' name of s_ins enrolled in
    """
    class_ids = DataModel.Relationship.objects.filter(student_instance=student).values("class_instance")
    classes = DataModel.Class.objects.filter(pk__in=class_ids)
    return classes


def get_skills_descriptions_groups_by_class(student):
    enrolled_classes = get_enrolled_classes(student)
    skills_descriptions_groups_by_class = {}
    for c in enrolled_classes:
        description = DataModel.Description.objects.filter(student_instance=student, class_instance=c).first()
        skills = DataModel.Skill_label.objects.filter(student_instance=student, class_instance=c).first()
        group_id = DataModel.Relationship.objects.filter(student_instance=student, class_instance=c).values(
            "group_id").first()
        if group_id == -1:
            group = None
        else:
            group = DataModel.Group.objects.filter(group_id=1).first()
        skills_descriptions_groups_by_class[c] = {"description": description, "skills": skills, "group": group}
        return skills_descriptions_groups_by_class


def my_classes(request):
    """
    :param request:
    :return: a html contains a list of class
    """
    student = request.user
    skills_descriptions_groups_by_class = get_skills_descriptions_groups_by_class(student)
    return render(request, 'studentDashBoard.html',
                  {'skills_descriptions_groups_by_class': skills_descriptions_groups_by_class,
                   'created_class_list': get_my_created_classes(request.user)})


def edit_classes(request):
    skills_descriptions_groups_by_class = get_skills_descriptions_groups_by_class(request.user)
    if request.method == 'POST':
        for key in skills_descriptions_groups_by_class:
            description = skills_descriptions_groups_by_class[key]['description']
            skills = skills_descriptions_groups_by_class[key]['skills']
            description.description = request.POST["new_description_"+key.class_name]
            skills.label = request.POST["new_skills_"+key.class_name]
            description.save()
            skills.save()
        return HttpResponseRedirect('/myclasses')
    else:
        return render(request, 'classedit.html', {'skills_descriptions_groups_by_class': skills_descriptions_groups_by_class})


def classDelete(request):
    """
    :param request:
    :return: delete some class
    """
    request.method = 'POST'
    str = request.get_full_path()
    class_id = str.split("del")[-1]
    if getIDInstance().is_instructor:
        return HttpResponseRedirect('/dashboard/del'+class_id)
    else:
        # return render(request, 'studentDashBoard.html', {'myclasslist': getMyClass(getIDInstance())})
        return HttpResponseRedirect('/dashboard/del'+class_id)
