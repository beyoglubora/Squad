from django import forms
from data.models import Assignment, StudentUpload
from tempus_dominus.widgets import DatePicker, TimePicker, DateTimePicker
import datetime
from bootstrap_modal_forms.forms import BSModalForm


class Assignments_Boostrap_Form(BSModalForm):
    class Meta:
        model = Assignment
        fields = ['subject', 'description', 'due_date', 'class_instance']
        widgets = {
            'class_instance': forms.HiddenInput(),
            'due_date': DateTimePicker(
                options={
                    'minDate': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'format': "YYYY-MM-DD HH:mm"
                }
            )
        }


class AssignmentsForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ('subject', 'file', 'description', 'due_date', 'class_instance')
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'subject-class'}),
            'class_instance': forms.HiddenInput(),
            'description': forms.Textarea(attrs={'class': 'description-class'}),
            'due_date': DateTimePicker(
                options={
                    'minDate': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'format': "YYYY-MM-DD HH:mm",
                    'defaultDate': datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                }
            )
        }


class StudentUploadForm(forms.ModelForm):
    class Meta:
        model = StudentUpload
        fields = ('description', 'upload_file')
        widgets = {
            'description': forms.Textarea(attrs={'class': 'description-class'}),
            'upload_file': forms.FileInput(attrs={'class': 'assignment-upload-button'})
        }