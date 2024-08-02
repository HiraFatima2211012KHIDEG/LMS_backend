from django.contrib import admin
from .models.models import *

admin.site.register(Program)
admin.site.register(Course)
admin.site.register(Module)
admin.site.register(Content)
admin.site.register(ContentFile)
admin.site.register(Assignment)
admin.site.register(AssignmentSubmission)
admin.site.register(Grading)
