from django.http import HttpResponseRedirect
from django.shortcuts import render
from data.models import Class
from explore.forms import CreateClassForm


def explore_page(request):
    return render(request, 'explore.html', {'classes': Class.objects.all()})


def create_class(request):
    if request.method == 'POST':
        form = CreateClassForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.instructor_instance = request.user
            instance.save()
            return HttpResponseRedirect('/explore/')
    else:
        form = CreateClassForm()

    return render(request, 'create_class.html', {'form': form})
