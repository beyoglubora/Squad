from django import forms
from data.models import Account
from django.contrib.auth.forms import UserCreationForm


class CustomRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    profile_photo = forms.FileField(required=False)
    is_instructor = forms.BooleanField(required=False)

    class Meta:
        model = Account
        fields = ('first_name', 'last_name', 'email', 'profile_photo', 'is_instructor', 'password1', 'password2')
