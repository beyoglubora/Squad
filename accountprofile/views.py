from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from data import models as DataModel
from myclasses.views import getMyClass
from groups.views import enroll, check_enroll
import html


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


def listRequestedmine(request):
    # if (not getIDInstance()):
    #     messages.info(request, "You are not logged in!")
    #     return HttpResponseRedirect('/account/')
    list = getAllProfile(getIDInstance(request))
    same_one = True
    list_eclass_and_iclass = False
    return render(request, 'userprofile.html', {
        'fname': list[0],
        'lname': list[1],
        'email': list[2],
        'incins': list[3],
        'photo': list[4],
        'desins': list[5],
        'encins': list[6],
        'sins': list[7],
        'same_one': same_one,
        'listclass': list_eclass_and_iclass,
        'aggregator': list[8],
    })


def listRequested(request):
    explorer_id = getIDInstance(request).account_id
    uid = request.get_full_path().split('/account/')[-1]
    is_same_one = (str(explorer_id) == uid)
    list_eclass_and_iclass = (str(explorer_id) != uid)
    u_ins = DataModel.Account.objects.filter(account_id=uid)
    is_instructor = DataModel.Account.objects.filter(account_id=uid)[0].is_instructor
    if (not u_ins):
        messages.info(request, "No Such User")
        return HttpResponseRedirect('/account/')
    list = getAllProfile(u_ins[0])
    icins_empty = False
    if not list[3]:
        icins_empty = True
    return render(request, 'userprofile.html', {
        'fname': list[0],
        'lname': list[1],
        'email': list[2],
        'incins': list[3],
        'photo': list[4],
        'desins': list[5],
        'encins': list[6],
        'sins': list[7],
        'same_one': is_same_one,
        'listclass': list_eclass_and_iclass,
        'u_ins':u_ins,
        'aggregator': list[8],
        'is_instructor':is_instructor,
        'instruct_null':icins_empty
    })


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
