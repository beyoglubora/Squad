from django.http import HttpResponseRedirect
from django.shortcuts import render
from data import models as DataModel


def getIDInstance():
    """
    :return: current student instance who clicked
    """
    return DataModel.Account.objects.all()[2]


def getMyCreatedClasses(instructor):
    classes = DataModel.Class.objects.filter(instructor=instructor)
    return classes


def getMyEnrolledClasses(student):
    """
    :param s_ins: student_instance
    :return: a list of classes' name of s_ins enrolled in
    """
    classes = DataModel.Relationship.objects.filter(student_instance=student)
    return classes


def listRequested(request):
    """
    :param request:
    :return: a html contains a list of class
    """
    return render(request, 'studentDashBoard.html',
                  {'enrolled_class_list': getMyEnrolledClasses(request.user),
                   'created_class_list': getMyCreatedClasses(request.user)})


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
