from django.shortcuts import render
from data.models import Class
from django.http import JsonResponse


def explore_page(request):
    return render(request, 'explore.html', {'classes': Class.objects.all()})


def create_class(request):
    class_name = request.POST.get('class_name', None)
    class_description = request.POST.get('class_description', None)
    class_instance = Class()
    class_instance.class_name = class_name
    class_instance.description = class_description
    class_instance.instructor_instance = request.user
    try:
        class_instance.save()
    except:
        raise ValueError("This class already exists")
    class_instance.save()
    class_instance = Class.objects.last()
    data = {'status': "../groups/class/" + str(class_instance.class_id)}
    return JsonResponse(data)
