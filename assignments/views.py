from django.shortcuts import render
from assignments.forms import AssignmentsForm
from data.models import Class

# Create your views here.
def show(request):
    class_instance = Class.objects.first()
    if request.method == 'POST':
        form = AssignmentsForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
    else:
        form = AssignmentsForm(request.POST, request.FILES)
        return render(request, 'assignment.html',{
            'form': form,
            'ins': class_instance
        })