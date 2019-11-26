from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from assignments.forms import AssignmentsForm, StudentUploadForm, Assignments_Boostrap_Form
from data.models import Class, Assignment, Group, StudentUpload, AssignmentRelationship, Relationship
from django.urls import reverse_lazy


# Create your views here.
def assignment_main_page(request, class_pk):
    class_instance = Class.objects.filter(class_id=class_pk).first()
    if not class_instance:
        messages.info(request, "No Such Class")
        return HttpResponseRedirect("/groups/class/"+str(class_pk))
    if class_instance.instructor_instance != request.user:
        messages.info(request, "You are not the instructor of this class")
        return HttpResponseRedirect("/groups/class/" + str(class_pk))

    assignments_in_this_class = Assignment.objects.filter(class_instance=class_instance)

    if request.method == 'POST':
        form = AssignmentsForm(request.POST, request.FILES)
        if form.is_valid():
            a = form.save()

        return render(request, 'assignment_main_instructor.html', {
            'class_ins': class_instance,
            'assignments': assignments_in_this_class,
            'form': form,
        })
    else:
        form = AssignmentsForm(initial={'class_instance': class_instance})
        return render(request, 'assignment_main_instructor.html', {
            'class_ins': class_instance,
            'assignments': assignments_in_this_class,
            'form': form,
        })


def get_class_ins(request):
    return Class.objects.first()


def get_assignment_ins(request):
    return Assignment.objects.first()


def get_group_ins(request):
    return Group.objects.first()


def show(request):
    class_ins = get_class_ins(request)
    # for test
    if request.method == 'POST':
        form = AssignmentsForm(request.POST, request.FILES)
        print(222)
        if form.is_valid():
            print(form.cleaned_data['due_date'])

            print("1111")
            # a = form.save()

        # TODO: new return
        return render(request, 'assignment.html', {
            'form': form,
        })
    else:
        form = AssignmentsForm(initial={'class_instance': class_ins})
        return render(request, 'assignment.html', {
            'form': form,
        })


def show_student_upload(request):
    assignment_ins = get_assignment_ins(request)
    group_ins = get_group_ins(request)
    # for test
    if request.method == 'POST':
        form = StudentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            student_upload = form.save()
            print(student_upload.upload_file)

            temp_a_re = AssignmentRelationship.objects.filter(group_instance=group_ins,
                                                              assignment_instance=assignment_ins)
            if not temp_a_re:
                # this group hasn't uploaded file for this assignment
                new_a_re = AssignmentRelationship()
                new_a_re.student_upload_instance = student_upload
                new_a_re.group_instance = group_ins
                new_a_re.assignment_instance = assignment_ins
                new_a_re.save()
                print(new_a_re.upload_time)
                print(new_a_re.student_upload_instance.upload_file)

            else:
                # this group has already uploaded a file for this assignment
                exist_a_re = temp_a_re.first()
                old_student_upload = exist_a_re.student_upload_instance
                exist_a_re.student_upload_instance = student_upload
                exist_a_re.save()
                print(exist_a_re.upload_time)
                # delete the old one
                old_student_upload.delete()
                print(exist_a_re.student_upload_instance.upload_file)


        # TODO: new return
        return render(request, 'assignment.html', {
            'form': form,
        })
    else:
        form = StudentUploadForm()
        return render(request, 'student_upload.html', {
            'form': form,
        })


def show_assignment_detail(request, a_pk):
    """
    render to a detail page of an assignment, where instructor can see groups with their
    uploaded files
    :param request, a_pk:
    :return:
    """
    assignment_ins = Assignment.objects.filter(assignment_id=a_pk).first()
    if not assignment_ins:
        messages.info(request, "No Such Class")
        return HttpResponseRedirect("/explore")
    if assignment_ins.class_instance.instructor_instance != request.user:
        messages.info(request, "You are not the instructor of this class")
        return HttpResponseRedirect("/explore")

    ass_class_instance = assignment_ins.class_instance
    # get groups in this class
    groups = Group.objects.filter(class_instance=ass_class_instance)
    groups_assignment_dict = {}
    for group in groups:
        a_rel = AssignmentRelationship.objects.filter(group_instance=group,
                                                      assignment_instance=assignment_ins).first()
        if not a_rel:
            # this group has no file for this assignment
            groups_assignment_dict[group] = False
        else:
            groups_assignment_dict[group] = a_rel

    return render(request, 'assignment_detail_instructor.html', {
        'groups_rel_dic': groups_assignment_dict
    })


def show_assignment_group(request, group_pk):
    group_instance = Group.objects.filter(group_id=group_pk).first()
    if not group_instance:
        messages.info(request, "No Such Class")
        return HttpResponseRedirect("/explore")
    relationship_instance = Relationship.objects.filter(group_id=group_pk, student_instance=request.user).first()
    if not relationship_instance:
        messages.info(request, "You are not in that Group")
        return HttpResponseRedirect("/explore")

    class_instance = group_instance.class_instance
    # find all assignment for this class
    assignment_in_class = Assignment.objects.filter(class_instance=class_instance)
    assignment_group_dict = {}
    for a in assignment_in_class:
        a_rel = AssignmentRelationship.objects.filter(group_instance=group_instance,
                                                      assignment_instance=a).first()
        if not a_rel:
            # this group has no file for this assignment
            assignment_group_dict[a] = False
        else:
            assignment_group_dict[a] = a_rel

    return render(request, 'assignment_in_group.html', {
        'assignment_rel_dic': assignment_group_dict
    })
