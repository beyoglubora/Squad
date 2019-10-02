from django.shortcuts import render
from django.views import generic
from . import models


class Explore(generic.CreateView):
    template_name = "home.html"
    fields = '__all__'

    def get_queryset(self):
        return models.Class.objects.order_by('id')
