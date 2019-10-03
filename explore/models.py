from django.db import models
from django.core.validators import validate_comma_separated_integer_list


class Class(models.Model):
    groups = models.CharField(validators=[validate_comma_separated_integer_list], max_length=200, blank=True)
    students = models.CharField(validators=[validate_comma_separated_integer_list], max_length=200, blank=True)
    name = models.CharField(max_length=200, unique=True, default=None)
    description = models.CharField(max_length=2000, default=None)
    instructor = models.IntegerField(default=None)

    class Meta:
        verbose_name_plural = "Classes"
