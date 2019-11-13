from django.urls import reverse_lazy
from django.views import generic
from accounts.forms import CustomRegistrationForm
from django.http import HttpResponseRedirect


class SignUp(generic.CreateView):
    form_class = CustomRegistrationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'


def jump_to_login(request):
    return HttpResponseRedirect('/accounts/login/')
