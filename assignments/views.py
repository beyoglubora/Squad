from django.http import HttpResponseRedirect
from django.shortcuts import render
from assignments.forms import AssignmentsForm
from data.models import Class

# Create your views here.
def show(request):
    class_ins = Class.objects.first()
    # for test
    if request.method == 'POST':
        form = AssignmentsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()

        # TODO: new return
        return render(request, 'assignment.html', {
            'form': form,
        })
    else:
        form = AssignmentsForm(initial={'class_instance': class_ins})
        return render(request, 'assignment.html',{
            'form': form,
        })