from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth import login, authenticate
from accounts.forms import CustomRegistrationForm
from django.http import HttpResponseRedirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.http import HttpResponse
from django.shortcuts import render, redirect
from data.models import Account
from groups.views import EmailThread, send_mail
from Squad.settings import EMAIL_HOST_USER

def signup(request):
    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate your Squad account.'
            message = render_to_string('acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            send_mail(mail_subject, message, EMAIL_HOST_USER, [to_email])
            # email = EmailMessage(
            #     mail_subject, message, to=[to_email]
            # )
            # email.send()
            return HttpResponseRedirect("/accounts/activate/")
    else:
        form = CustomRegistrationForm()
    return render(request, 'signup.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = Account.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return render(request, 'account_activation_confirm.html', {"valid": True})
    else:
        return render(request, 'account_activation_confirm.html', {"valid": False})


def account_activation(request):
    return render(request, 'account_activation.html')


def jump_to_login(request):
    return HttpResponseRedirect('/accounts/login/')
