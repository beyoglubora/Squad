from django.http import JsonResponse
from django.shortcuts import render
import data as DataModel

def show_messages(request):
    return render(request, 'discussion.html')


def create_post(request):
    # class post -> -5
    # group post -> group id

    return JsonResponse({"result": True})


def delete_post(request):
    # creator and instructor
    # create parent -> all gone

    return JsonResponse({"result": True})


def edit_post(request):
    # only creator can edit
    return JsonResponse({"result": True})
