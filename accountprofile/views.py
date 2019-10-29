from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from data import models as DataModel
from myclasses.views import getMyClass


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
    group_by_list = {}
    for tc in skill:
        cname = tc.class_instance.class_name
        if not cname in group_by_list.keys():
            group_by_list[cname] = []
            group_by_list[cname].append(tc.label)
        else:
            group_by_list[cname].append(tc.label)
    skill = group_by_list
    list = [fname, lname, email, is_instructor_of,
            photo, descrip_by_class, class_enroll,
            skill]
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
        'listclass': list_eclass_and_iclass
    })


def listRequested(request):
    explorer_id = getIDInstance(request).account_id
    uid = request.get_full_path().split('/account/')[-1]
    is_same_one = (str(explorer_id) == uid)
    list_eclass_and_iclass = (str(explorer_id) != uid)
    u_ins = DataModel.Account.objects.filter(account_id=uid)
    if (not u_ins):
        messages.info(request, "No Such User")
        return HttpResponseRedirect('/account/')
    list = getAllProfile(u_ins[0])
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
        'listclass': list_eclass_and_iclass
    })


def changProfile(request):
    s_ins = getIDInstance(request)
    list = getAllProfile(s_ins)
    if request.method == 'POST':
        s_ins.first_name = request.POST["newfname"]
        s_ins.last_name = request.POST["newlname"]
        if (request.POST['newphoto']):
            s_ins.profile_photo = request.POST['newphoto']
        s_ins.save()
        for dc in list[5]:
            dc.description = request.POST["des" + dc.class_instance.class_name]
            dc.save()
        dict_skills = list[7]
        for key in dict_skills:
            for value in dict_skills[key]:
                skill_ins = DataModel.Skill_label.objects.filter(class_instance__class_name=key, label=value)[0]
                skill_ins.label = request.POST["tags"+value]
                skill_ins.save()

        return HttpResponseRedirect('/account')

    else:
        return render(request, 'modify_profile.html', {
            'fname': list[0],
            'lname': list[1],
            'incins': list[3],
            'photo': list[4],
            'desins': list[5],
            'encins': list[6],
            'sins': list[7]
        })
