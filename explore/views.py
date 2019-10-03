from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic
from . import models
from explore.forms import CreateClassForm


def explore_page(request):
    return render(request, 'explore.html', {'classes': models.Class.objects.all()})


def create_class(request):
    if request.method == 'POST':
        form = CreateClassForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.instructor = request.user.pk
            instance.save()
            return HttpResponseRedirect('/explore/')
    else:
        form = CreateClassForm()

    return render(request, 'create_class.html', {'form': form})
