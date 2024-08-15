from django.contrib import admin
from .models.models import *
from .models.program_model import *

admin.site.register(Program)
admin.site.register(Course)
admin.site.register(Module)
admin.site.register(ContentFile)
admin.site.register(Assignment)
admin.site.register(AssignmentSubmission)
admin.site.register(Grading)
admin.site.register(Quizzes)
admin.site.register(QuizSubmission)
admin.site.register(QuizGrading)
admin.site.register(Project)
admin.site.register(ProjectSubmission)
admin.site.register(ProjectGrading)
admin.site.register(Exam)
admin.site.register(ExamSubmission)
admin.site.register(ExamGrading)