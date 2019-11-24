from django import forms
from data.models import Assignment
from tempus_dominus.widgets import DatePicker, TimePicker, DateTimePicker
import datetime


class AssignmentsForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ('subject', 'description', 'due_date', 'class_instance')
        widgets = {
            'class_instance': forms.HiddenInput(),
            'due_date': DateTimePicker(
                options={
                    'minDate': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'format': "YYYY-MM-DD HH:mm"
                }
            )
        }
