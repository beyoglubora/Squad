from django import forms
from data.models import Assignment

class AssignmentsForm(forms.ModelForm):

    class Meta:
        model = Assignment
        fields = ('subject', 'description', 'due_date')
