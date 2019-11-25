from django.contrib import admin

# Register your models here.

from .models import Account
from .models import Class
from .models import Notification
from .models import Group
from .models import Relationship
from .models import Skill_label
from .models import Description
from .models import Messages
from .models import Assignment
from .models import StudentUpload
from .models import AssignmentRelationship

admin.site.register(Account)
admin.site.register(Class)
admin.site.register(Notification)
admin.site.register(Group)
admin.site.register(Relationship)
admin.site.register(Skill_label)
admin.site.register(Description)
admin.site.register(Messages)
admin.site.register(Assignment)
admin.site.register(StudentUpload)
admin.site.register(AssignmentRelationship)