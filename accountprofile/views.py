from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from data import models as DataModel
from myclasses.views import getMyClass
from groups.views import enroll, check_enroll
import html
import re



def getIDInstance(request):
    """
    :return: current student instance who clicked
    """
    user_email = request.user.email
    s_ins = DataModel.Account.objects.filter(email=user_email)[0]
    return s_ins


def getAllProfile(s_ins):
    """
    :param s_ins: user instance for retrieve profiles
    :return: all profiles user has
    """
    fname = s_ins.first_name
    lname = s_ins.last_name
    email = s_ins.email
    is_instructor_of = DataModel.Class.objects.filter(instructor_instance=s_ins)
    photo = s_ins.profile_photo
    descrip_by_class = DataModel.Description.objects.filter(student_instance=s_ins)
    class_enroll = getMyClass(s_ins)
    skill = DataModel.Skill_label.objects.filter(student_instance=s_ins)
    skill2 = skill
    group_by_list = {}
    for tc in skill:
        cname = tc.class_instance.class_name
        if not cname in group_by_list.keys():
            group_by_list[cname] = []
            group_by_list[cname].append(str(tc.label))
        else:
            group_by_list[cname].append(str(tc.label))
    skill = group_by_list
    des_tag_aggby_class = {}
    for tc in descrip_by_class:
        cname = tc.class_instance.class_name
        t = ()
        des_tag_aggby_class[cname] = t + (tc.description,) + (group_by_list[cname],) + (tc.class_instance.class_id,)
    list = [fname, lname, email, is_instructor_of,
            photo, descrip_by_class, class_enroll,
            skill, des_tag_aggby_class]
    return list


def listRequested(request):
    user_id = request.get_full_path().split('/account/')[-1]
    own_profile = False
    if user_id == request.user.pk:
        own_profile = True
    student_instance = DataModel.Account.objects.filter(account_id=user_id).first()
    classes = {}
    if student_instance.is_instructor:
        instructing_classes = DataModel.Class.objects.filter(instructor_instance=student_instance)
        for c in instructing_classes:
            d = {}
            d['description'] = c.description
            classes[c] = d
    else:
        relations = DataModel.Relationship.objects.filter(student_instance=student_instance)
        for relation in relations:
            d = {}
            d['description'] = DataModel.Description.objects.filter(student_instance=relation.student_instance,
                                                                    class_instance=relation.class_instance).first().description
            d['skills'] = DataModel.Skill_label.objects.filter(student_instance=relation.student_instance,
                                                               class_instance=relation.class_instance).first().label.split(",")
            d['skills_display'] = ", ".join(d['skills'])
            classes[relation.class_instance] = d

    return render(request, 'userprofile.html', {'user_instance': student_instance, 'classes': classes, 'own_profile': own_profile})


def changProfile(request):
    s_ins = getIDInstance(request)
    list = getAllProfile(s_ins)
    if request.method == 'POST':
        s_ins.first_name = request.POST["newfname"]
        s_ins.last_name = request.POST["newlname"]
        if 'newphoto' in request.FILES:
            s_ins.profile_photo = request.FILES['newphoto']
        s_ins.save()
        '''
        for dc in list[5]:
            dc.description = request.POST["des" + dc.class_instance.class_name]
            dc.save()
        dict_skills = list[7]
        for key in dict_skills:
            for value in dict_skills[key]:
                skill_ins = DataModel.Skill_label.objects.filter(student_instance=s_ins,class_instance__class_name=key, label=value)[0]
                skill_ins.label = request.POST["tags"+value]
                skill_ins.save()
        '''
        return HttpResponseRedirect('/account')

    else:
        return render(request, 'modify_profile.html', {
            'fname': list[0],
            'lname': list[1],
            'incins': list[3],
            'photo': list[4],
            'desins': list[5],
            'encins': list[6],
            'sins': list[7],
            'aggregator': list[8]
        })


def edit_enroll(request):
    description = request.POST.get('description', None)
    skills = request.POST.getlist('skills[]', None)
    skills = ", ".join(skills)
    class_id = request.POST.get('class_id', None)
    class_instance = DataModel.Class.objects.filter(class_id=class_id).first()
    skill_label = DataModel.Skill_label.objects.filter(student_instance=request.user, class_instance=class_instance).first()
    skill_label.label = skills
    skill_label.save()
    description_instance = DataModel.Description.objects.filter(student_instance=request.user, class_instance=class_instance).first()
    description_instance.description = description
    description_instance.save()
    data={"message": "Successfully enrolled in class"}
    return JsonResponse(data)


def edit_class(request):
    class_id = request.POST.get('class_id')
    class_name = request.POST.get('class_name', None)
    class_description = request.POST.get('class_description', None)
    print(class_id)
    print(class_name)
    print(class_description)
    class_instance = DataModel.Class.objects.filter(class_id=class_id).first()
    class_instance.class_name = class_name
    class_instance.description = class_description
    try:
        class_instance.save()
    except:
        raise ValueError("This class already exists")
    return JsonResponse({"message":"Successfully edited class"})


def edit_profile(request):
    first_name = request.POST.get("first_name")
    last_name = request.POST.get("last_name")
    email = request.POST.get("email")
    profile_photo = request.FILES.get("profile_photo")
    pattern = re.compile("^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$")
    if pattern.match(email):
        student_instance = DataModel.Account.objects.filter(account_id=request.user.pk).first()
        if first_name and not first_name.isspace():
            student_instance.first_name = first_name
        if last_name and not last_name.isspace():
            student_instance.last_name = last_name
        student_instance.email = email
        if profile_photo:
            student_instance.profile_photo = profile_photo
        student_instance.save()
        return JsonResponse({"data": "successfully updated users profile"})
    else:
        response = JsonResponse({"data": "user did not provide valid email address"})
        response.status_code = 403
        return response


def delete_class(request):
    class_id = request.POST.get("class_id")
    DataModel.Class.objects.filter(class_id=class_id).delete()
    return JsonResponse({"message": "Successfully deleted class"})


def changebyclass(request):
    class_id = request.get_full_path().split('/account/class/')[-1]
    Relation_ins = DataModel.Relationship.objects.filter(class_instance__class_id=class_id, student_instance=request.user)
    invalid = False
    if not Relation_ins:
        messages.info(request, "You are not in this class")
        return HttpResponseRedirect('/account/')
    des_ins = DataModel.Description.objects.filter(class_instance__class_id=class_id, student_instance=request.user)
    skill_ins = DataModel.Skill_label.objects.filter(class_instance__class_id=class_id, student_instance=request.user)
    if request.method == 'POST':
        skill_set = ""
        for key in request.POST:
            if "skill_set" in key:
                skill_set += request.POST[key] + ";"
        skill_set = skill_set[:-1]
        description = request.POST["description"]
        if check_enroll(skill_set, description):
            des_first = des_ins[0]
            s_first = skill_ins[0]
            des_first.description = description
            des_first.save()
            s_first.label = skill_set
            s_first.save()
            return HttpResponseRedirect('/account/')
        else:
            invalid = True
            des_string = des_ins[0].description
            multi_string = skill_ins[0].label.split(";")
            return render(request, 'changebyclass.html', {
                'rel_ins': Relation_ins,
                'des_string': des_string,
                'skill_ins': skill_ins,
                'invalid': invalid,
                'skill_strings': multi_string
            })
    else:
        des_string = des_ins[0].description
        multi_string = skill_ins[0].label.split(";")
        return render(request, 'changebyclass.html', {
            'rel_ins':Relation_ins,
            'des_string':des_string,
            'skill_ins':skill_ins,
            'invalid': invalid,
            'skill_strings':multi_string
        })
