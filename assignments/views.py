from django.http import HttpResponseRedirect
from django.shortcuts import render
from assignments.forms import AssignmentsForm, StudentUploadForm
from data.models import Class, Assignment, Group, StudentUpload, AssignmentRelationship

# Create your views here.
def assignment_main_page(request):
    class_id = request.GET.get('class_id')
    class_instance = Class.objects.filter(class_id=class_id).first()
    return render(request, 'assignment_main_instructor.html',{
        'class_ins': class_instance
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