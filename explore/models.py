from django.db import models
from django.core.validators import validate_comma_separated_integer_list

class Class(models.Model):
    groups = models.CharField(validators=[validate_comma_separated_integer_list], max_length=200, default=[])
    students = models.CharField(validators=[validate_comma_separated_integer_list], max_length=200, default=[])

