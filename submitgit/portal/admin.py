from django.contrib import admin
from .models import Course, Repository, Assignment
from .models import Submission


admin.site.register(Course)
admin.site.register(Repository)
admin.site.register(Assignment)
admin.site.register(Submission)
