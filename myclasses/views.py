from django.http import HttpResponseRedirect
from django.shortcuts import render
from data import models as DataModel


def getIDInstance(request):
    """
    :return: current student instance who clicked
    """
    user_email = request.user.email
    s_ins = DataModel.Account.objects.filter(email=user_email)[0]
    return s_ins

def getMyClass(s_ins):
    """
    :param s_ins: student_instance
    :return: a list of classes' name of s_ins enrolled in
    """
    classes = DataModel.Relationship.objects.filter(student_instance=s_ins)
    ls = []
    for c in classes:
        ls.append(c.class_instance)
        # if ls is null
    return ls

def listRequested(request):
    """
    :param request:
    :return: a html contains a list of class
    """
    s_ins = getIDInstance(request)
    group_instance = DataModel.Relationship.objects.filter(student_instance=s_ins)
    is_instructor_of = DataModel.Class.objects.filter(instructor_instance=s_ins)
    if request.method == 'POST':
        pass
    else:
        return render(request, 'studentDashBoard.html',
                    {'myclasslist': getMyClass(s_ins),
                    'user_is_instructor': s_ins.is_instructor,
                    'is_instructor_of': is_instructor_of,
                    'groups':group_instance})

def classDelete(request):
    """
    :param request:
    :return: delete some class
    """
    str = request.get_full_path()
    class_id = str.split("del")[-1]
    if getIDInstance(request).is_instructor:
        DataModel.Class.objects.filter(class_id=class_id).delete()
        return HttpResponseRedirect('/dashboard/')
    else:
        return HttpResponseRedirect('/dashboard')