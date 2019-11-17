from django.shortcuts import render

def show_messages(request):
    return render(request, 'discussion.html')
