from django import forms
from data.models import Assignment

class AssignmentsForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['due_date'].widget.attrs.update({
            'class': 'form-control datetimepicker-input',
            'data-target': '#datetimepicker1'
        })

    class Meta:
        model = Assignment
        fields = ('subject', 'description', 'due_date', 'class_instance')
        widgets = {
            'class_instance': forms.HiddenInput()
        }
