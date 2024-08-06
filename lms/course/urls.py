from django.urls import path
from .views.views import *
from .views.content_view import *
from .views.assignment_view import *
from .views.quizzes_view import *
from .views.project_view import *
from .views.exam_view import *

urlpatterns = [
    path('programs/', ProgramListCreateAPIView.as_view(), name='program-list-create'),
    path('programs/<int:pk>/', ProgramDetailAPIView.as_view(), name='program-detail'),
    path('courses/', CourseListCreateAPIView.as_view(), name='course-list-create'),
    path('courses/<int:pk>/', CourseDetailAPIView.as_view(), name='course-detail'),
    path('modules/', ModuleListCreateAPIView.as_view(), name='module-list-create'),
    path('modules/<int:pk>/', ModuleDetailAPIView.as_view(), name='module-detail'),
    path('contents/', ContentListCreateAPIView.as_view(), name='content-list-create'),
    path('contents/<int:pk>/', ContentDetailAPIView.as_view(), name='content-detail'),
    path('content_files/', ContentFileListCreateAPIView.as_view(), name='content-file-list-create'),
    path('content_files/<int:pk>/', ContentFileDetailAPIView.as_view(), name='content-file-detail'),
    path('toggle_activeinactive/<str:model_name>/<int:pk>/', ToggleActiveStatusAPIView.as_view(), name='toggle_active_status'),
    path('toggle_delete/<str:model_name>/<int:pk>/', ToggleActiveDeleteStatusAPIView.as_view(), name='toggle_active_status'),
    path('assignments/', AssignmentListCreateAPIView.as_view(), name='assignment-list-create'),
    path('assignments/<int:pk>/', AssignmentDetailAPIView.as_view(), name='assignment-detail'),
    path('submissions/', AssignmentSubmissionCreateAPIView.as_view(), name='submission-create'),
    path('submissions/<int:pk>/', AssignmentSubmissionDetailAPIView.as_view(), name='submission-detail'),
    path('assignments_grading/', AssignmentGradingListCreateAPIView.as_view(), name='grade-assignment'),
    path('assignments_grading/<int:pk>/', AssignmentGradingDetailAPIView.as_view(), name='grading-detail'),
    path('assignments/course/<int:course_id>/', AssignmentsByCourseIDAPIView.as_view(), name='assignments-by-course-id'),
    path('assignments/<int:assignment_id>/submissions/', UsersWhoSubmittedAssignmentAPIView.as_view(), name='users-who-submitted-assignment'),
    path('quizzes/', QuizListCreateAPIView.as_view(), name='quiz-list-create'),
    path('quizzes/<int:pk>/', QuizDetailAPIView.as_view(), name='quiz-detail'),
    path('quiz_submissions/', QuizSubmissionCreateAPIView.as_view(), name='quiz_submission_list_create'),
    path('quiz_submissions/<int:pk>/', QuizSubmissionDetailAPIView.as_view(), name='quiz_submission_detail'),
    path('quiz_grading/', QuizGradingListCreateAPIVieww.as_view(), name='quiz-grading-create'),
    path('quiz_grading/<int:pk>/', QuizGradingDetailAPIView.as_view(), name='quiz-grading-detail'),
    path('projects/', ProjectListCreateAPIView.as_view(), name='project-list-create'),
    path('projects/<int:pk>/', ProjectDetailAPIView.as_view(), name='project-detail'),
    path('project_submissions/', ProjectSubmissionListCreateAPIView.as_view(), name='project-submission-list-create'),
    path('project_submissions/<int:pk>/', ProjectSubmissionDetailAPIView.as_view(), name='project-submission-detail'),
    path('project_gradings/', ProjectGradingListCreateAPIView.as_view(), name='project-grading-list-create'),
    path('project_gradings/<int:pk>/', ProjectGradingDetailAPIView.as_view(), name='project-grading-detail'),
    path('exams/', ExamListCreateAPIView.as_view(), name='exam-list-create'),
    path('exams/<int:pk>/', ExamDetailAPIView.as_view(), name='exam-detail'),
    path('exam_submissions/', ExamSubmissionListCreateAPIView.as_view(), name='exam-submission-list-create'),
    path('exam_submissions/<int:pk>/', ExamSubmissionDetailAPIView.as_view(), name='exam-submission-detail'),
    path('exam_gradings/', ExamGradingListCreateAPIView.as_view(), name='exam-grading-list-create'),
    path('exam_gradings/<int:pk>/', ExamGradingDetailAPIView.as_view(), name='exam-grading-detail'),
]
