from django import forms
from data.models import Class


class CreateClassForm(forms.ModelForm):
    class_name = forms.CharField(required=True, max_length=200)
    description = forms.CharField(required=False, max_length=2000)

    class Meta:
        model = Class
        fields = ('class_name', 'description')


