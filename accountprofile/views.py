from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from data import models as DataModel
from myclasses.views import get_skills_descriptions_groups_by_class


def my_profile(request):
    student_model = request.user
    return render(request, 'userprofile.html', {'student_model': student_model})


def other_profile(request):
    student_id = request.get_full_path().split('/')[-1]
    student = DataModel.Account.objects.filter(account_id=student_id).first()
    if not student:
        messages.info(request, "No Such User")
        return HttpResponseRedirect('/account/')
    skills_description_groups_by_class = get_skills_descriptions_groups_by_class(student)
    instructing_classes = DataModel.Class.objects.filter(instructor=student)
    print(skills_description_groups_by_class)
    return render(request, 'userprofile.html', {
        'student_model': student,
        'instructing_classes': instructing_classes,
        'skills_descriptions_groups_by_class': skills_description_groups_by_class
    })


def change_profile(request):
    student = request.user
    instructor_for_classes = DataModel.Class.objects.filter(instructor=student)
    enrolled_class_ids = DataModel.Relationship.objects.filter(student_instance=student).values("class_instance")
    enrolled_classes = DataModel.Class.objects.filter(pk__in=enrolled_class_ids)
    skills_and_descriptions_by_class = {}
    for c in enrolled_classes:
        description = DataModel.Description.objects.filter(student_instance=student, class_instance=c).first()
        skills = DataModel.Skill_label.objects.filter(student_instance=student, class_instance=c).first()
        skills_and_descriptions_by_class[c] = {"description": description, "skills": skills}

    if request.method == 'POST':
        student.first_name = request.POST["new_first_name"]
        student.last_name = request.POST["new_last_name"]
        student.email = request.POST["new_email"]
        if request.POST['new_photo']:
            student.photo = request.POST['new_photo']
        student.save()
        return HttpResponseRedirect('/accountprofile')
    else:
        return render(request, 'modify_profile.html', {
            'instructor_for_classes': instructor_for_classes,
            'skills_and_description_by_class': skills_and_descriptions_by_class,
        })
