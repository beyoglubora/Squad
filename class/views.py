from django.shortcuts import render
from data import models as DataModel

# Create your views here.

def display_all_classes(request):
    classes = DataModel.Class.objects.all()
    return render(request, 'class.html', {'classes': classes})