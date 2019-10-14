from django.db import models

# Create your models here.


class Account(models.Model):
    account_id = models.BigAutoField(primary_key=True)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    email = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=30)
    is_instructor = models.BooleanField(default=False)
    photo = models.FileField(default=None, blank=True)
    



class Class(models.Model):
    class_id = models.BigAutoField(primary_key=True)
    class_name = models.CharField(max_length=20)
    description = models.TextField()
    instructor_instance = models.ForeignKey('Account', on_delete=models.CASCADE)

    @classmethod
    def add_class(cls, class_name, instructor):
        temp = Class(class_name=class_name, instructor_instance=instructor)
        temp.save()
        return True


class Notification(models.Model):
    notification_id = models.BigAutoField(primary_key=True)
    class_instance = models.ForeignKey('Class', on_delete=models.CASCADE)
    sender_instance = models.ForeignKey('Account', on_delete=models.CASCADE, related_name='send_Account')
    receiver_instance = models.ForeignKey('Account', on_delete=models.CASCADE, related_name='receiver_Account')
    status = models.IntegerField()
    read = models.BooleanField()


class Group(models.Model):
    group_id = models.BigIntegerField(primary_key=True)  # It's a sql type ForeignKey referred to notification_id
    group_name = models.CharField(max_length=50, default='')


class Relationship(models.Model):
    student_instance = models.ForeignKey('Account', on_delete=models.CASCADE)
    class_instance = models.ForeignKey('Class', on_delete=models.CASCADE)
    group_id = models.BigIntegerField(default=-1)  # It's a sql type ForeignKey referred to notification_id

    def __str__(self):
        return 'account ' + str(self.student_instance.account_id) + ' in class ' + \
               str(self.class_instance.class_id) + ' ' + self.class_instance.class_name + ' group ' + \
               str(self.group_id)


class Skill_label(models.Model):
    student_instance = models.ForeignKey('Account', on_delete=models.CASCADE)
    class_instance = models.ForeignKey('Class', on_delete=models.CASCADE)
    label = models.CharField(max_length=20)

    def __str__(self):
        return self.label + ' ' + \
               self.student_instance.first_name + ' ' + \
               self.student_instance.last_name


# a student's self description in a class
class Description(models.Model):
    student_instance = models.ForeignKey('Account', on_delete=models.CASCADE)
    class_instance = models.ForeignKey('Class', on_delete=models.CASCADE, related_name='+')
    description = models.TextField()


