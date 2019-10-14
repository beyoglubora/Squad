from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from data import models as DataModel
from myclasses.views import getMyClass

def getIDInstance():
    """
    :return: current student instance who clicked
    """
    return DataModel.Account.objects.all()[2]
def getAllProfile(s_ins):
    """
    :param s_ins: user instance for retrieve profiles
    :return: all profiles user has
    """
    fname = s_ins.first_name
    lname = s_ins.last_name
    email = s_ins.email
    is_instructor_of = DataModel.Class.objects.filter(instructor_instance=s_ins)
    photo = s_ins.photo
    descrip_by_class = DataModel.Description.objects.filter(student_instance=s_ins)
    class_enroll = getMyClass(s_ins)
    skill = DataModel.Skill_label.objects.filter(student_instance=s_ins)
    list = [fname, lname, email, is_instructor_of,
            photo, descrip_by_class, class_enroll,
            skill]
    return list

def listRequestedmine(request):
    # if (not getIDInstance()):
    #     messages.info(request, "You are not logged in!")
    #     return HttpResponseRedirect('/account/')
    list = getAllProfile(getIDInstance())
    return render(request, 'userprofile.html', {
        'fname':list[0],
        'lname':list[1],
        'email':list[2],
        'incins':list[3],
        'photo':list[4],
        'desins':list[5],
        'encins':list[6],
        'sins':list[7]
    })

def listRequested(request):
    uid = request.get_full_path().split('/account/')[-1]
    u_ins = DataModel.Account.objects.filter(account_id=uid)
    if (not u_ins):
        messages.info(request, "No Such User")
        return HttpResponseRedirect('/account/')
    list = getAllProfile(u_ins[0])
    return render(request, 'userprofile.html', {
        'fname':list[0],
        'lname':list[1],
        'email':list[2],
        'incins':list[3],
        'photo':list[4],
        'desins':list[5],
        'encins':list[6],
        'sins':list[7]
    })

def changProfile(request):
    s_ins = getIDInstance()
    list = getAllProfile(s_ins)
    if request.method == 'POST':
        s_ins.first_name = request.POST["newfname"]
        s_ins.last_name = request.POST["newlname"]
        s_ins.email = request.POST["newemail"]
        if (request.POST['newphoto']):
            s_ins.photo = request.POST['newphoto']
        s_ins.save()
        for dc in list[5]:
            dc.description = request.POST["new"+dc.class_instance.class_name]
            dc.save()
        for tc in list[7]:
            tc.label = request.POST["new"+tc.class_instance.class_name]
            tc.save()

        return HttpResponseRedirect('/account')

    else:
        return render(request, 'modify_profile.html', {
            'fname': list[0],
            'lname': list[1],
            'email': list[2],
            'incins': list[3],
            'photo': list[4],
            'desins': list[5],
            'encins': list[6],
            'sins': list[7]
        })
