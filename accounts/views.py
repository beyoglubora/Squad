from django.urls import reverse_lazy
from django.views import generic
from accounts.forms import CustomRegistrationForm


class SignUp(generic.CreateView):
    form_class = CustomRegistrationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'
