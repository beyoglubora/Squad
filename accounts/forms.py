from django import forms
from accounts.models import Account, MyAccountManager
from django.contrib.auth.forms import UserCreationForm


class CustomRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    profile_photo = forms.FileField(required=False)
    is_instructor = forms.BooleanField(required=False)

    class Meta:
        model = Account
        fields = ('username', 'email', 'profile_photo', 'is_instructor', 'password1', 'password2')
