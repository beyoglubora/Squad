from django.http import HttpResponseRedirect
from django.shortcuts import render
from data import models as DataModel
from django.contrib import messages

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
    ls = {}
    for c in classes:
        if c.group_id == -1:
            ls[c.class_instance] = -1
        else:
            group = DataModel.Group.objects.filter(group_id=c.group_id).first()
            ls[c.class_instance] = group
        # if ls is null
    return ls

def listRequested(request):
    """
    :param request:
    :return: a html contains a list of class
    """
    s_ins = getIDInstance(request)
    relationship_instance = DataModel.Relationship.objects.filter(student_instance=s_ins)
    group_list = []
    is_instructor_of = DataModel.Class.objects.filter(instructor_instance=s_ins)
    for re in relationship_instance:
        group_ins = DataModel.Group.objects.filter(group_id=re.group_id)
        if not group_ins:
            group_name = ""
        else:
            group_name = group_ins[0].group_name

        group_list.append((re, group_name))

    if request.method == 'POST':
        pass
    else:
        return render(request, 'studentDashBoard.html',
                    {'classes': getMyClass(s_ins),
                    'user_is_instructor': s_ins.is_instructor,
                    'is_instructor_of': is_instructor_of,
                    'groups':group_list})

def classDelete(request):
    """
    :param request:
    :return: delete some class
    """
    str = request.get_full_path()
    class_id = str.split("del")[-1]
    class_instance = DataModel.Class.objects.filter(class_id=class_id)
    if not class_instance:
        messages.info(request, "No Such Class to Delete")
        return HttpResponseRedirect('/dashboard/')
    is_instructor_of_the_class = class_instance[0].instructor_instance == request.user
    print(is_instructor_of_the_class)
    if getIDInstance(request).is_instructor and is_instructor_of_the_class:
        DataModel.Class.objects.filter(class_id=class_id).delete()
        return HttpResponseRedirect('/dashboard/')
    else:
        messages.info(request, "You are not the instructor of this class")
        return HttpResponseRedirect('/dashboard')