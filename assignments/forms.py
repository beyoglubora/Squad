from django import forms
from data.models import Assignment

class AssignmentsForm(forms.ModelForm):
    date = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control datetimepicker-input',
            'data-target': '#datetimepicker1'
        })
    )
    class Meta:
        model = Assignment
        fields = ('subject', 'description', 'due_date', 'class_instance')
        widgets = {
            'class_instance': forms.HiddenInput()
        }
