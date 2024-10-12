from django.urls import path
from .views.views import *
from .views.content_view import *
from .views.assignment_view import *
from .views.quizzes_view import *
from .views.project_view import *
from .views.exam_view import *
from .views.program_view import *
from .views.weightage_view import *



urlpatterns = [
    path('program-course', CreateProgramView.as_view(), name='program-course'),
    path('programs/', ProgramListCreateAPIView.as_view(), name='program-list-create'),
    path('programs/<int:pk>/', ProgramDetailAPIView.as_view(), name='program-detail'),

    path('programs/student/<str:registration_id>/', ProgramByRegistrationIDAPIView.as_view(), name='student-program'),
    path('programs/<int:program_id>/courses/', ProgramCoursesAPIView.as_view(), name='program-courses'),
    path('courses/', CourseListCreateAPIView.as_view(), name='course-list-create'),
    path('courses/<int:pk>/', CourseDetailAPIView.as_view(), name='course-detail'),
    path('courses/<int:course_id>/modules/session/<int:session_id>/', CourseModulesAPIView.as_view(), name='course-modules'),
    path('modules/', ModuleListCreateAPIView.as_view(), name='module-list-create'),
    path('modules/<int:pk>/', ModuleDetailAPIView.as_view(), name='module-detail'),
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
    path('assignments/course/<int:course_id>/session/<int:session_id>/', AssignmentsByCourseIDAPIView.as_view(), name='assignments-by-course-id'),

    path('assignments/<int:assignment_id>/courses/<int:course_id>/sessions/<int:session_id>/students/',
        AssignmentStudentListView.as_view(),
        name='assignment-student-list'
    ),
    path('assignments/<int:course_id>/course/session/<int:session_id>/<str:registration_id>/total_score/', StudentScoresSummaryAPIView.as_view(), name='users-score-assignment'),
    path('programs/<str:session_ids>/students/<str:registration_id>/pending-assignments/', UnifiedPendingItemsView.as_view(), name='pending-assignments'),
    path('assignments/<int:course_id>/session/<int:session_id>/student/<str:registration_id>/', AssignmentDetailView.as_view(), name='assignment-detail'),

    # path('assignments/<str:registration_id>/submissions/', StudentsWhoSubmittedAssignmentAPIView.as_view(), name='users-who-submitted-assignment'),
    # path('assignments/<int:assignment_id>/students/', StudentsListSubmittedAssignmentAPIView.as_view(), name='users-list-submitted-assignment'),
   
    path('quizzes/', QuizListCreateAPIView.as_view(), name='quiz-list-create'),
    path('quizzes/<int:pk>/', QuizDetailAPIView.as_view(), name='quiz-detail'),
    path('quiz_submissions/', QuizSubmissionCreateAPIView.as_view(), name='quiz_submission_list_create'),
    path('quiz_submissions/<int:pk>/', QuizSubmissionDetailAPIView.as_view(), name='quiz_submission_detail'),
    path('quiz_grading/', QuizGradingListCreateAPIVieww.as_view(), name='quiz-grading-create'),
    path('quiz_grading/<int:pk>/', QuizGradingDetailAPIView.as_view(), name='quiz-grading-detail'),
    path('quizzes/<int:course_id>/session/<int:session_id>/student/<str:registration_id>/', QuizDetailView.as_view(), name='quiz-detail'),

    # path('quizzes/<int:course_id>/student/<str:registration_id>/', QuizDetailView.as_view(), name='quiz-detail'),
    # path('quizzes/course/<int:course_id>/', QuizzesByCourseIDAPIView.as_view(), name='quizzes-by-course-id'),
    path('quizzes/course/<int:course_id>/session/<int:session_id>/', QuizzesByCourseIDAPIView.as_view(), name='quizzes-by-course-id'),
    # path('courses/<int:course_id>/quizzes/<int:quiz_id>/students/', QuizStudentListView.as_view(), name='quiz-student-list'),
    # path(
    #     'quizzes/<int:quiz_id>/courses/<int:course_id>/sessions/<int:session_id>/students/',
    #     QuizStudentListView.as_view(),
    #     name='quiz-student-list'
    # ),
    path(
    'quizzes/<int:quiz_id>/courses/<int:course_id>/sessions/<int:session_id>/students/',
    QuizStudentListView.as_view(),
    name='quiz-student-list'
    ),
    path('projects/', ProjectListCreateAPIView.as_view(), name='project-list-create'),
    path('projects/<int:pk>/', ProjectDetailAPIView.as_view(), name='project-detail'),
    path('project_submissions/', ProjectSubmissionListCreateAPIView.as_view(), name='project-submission-list-create'),
    path('project_submissions/<int:pk>/', ProjectSubmissionDetailAPIView.as_view(), name='project-submission-detail'),
    path('project_gradings/', ProjectGradingListCreateAPIView.as_view(), name='project-grading-list-create'),
    path('project_gradings/<int:pk>/', ProjectGradingDetailAPIView.as_view(), name='project-grading-detail'),
    # path('projects/course/<int:course_id>/', ProjectsByCourseIDAPIView.as_view(), name='projects-by-course-id'),
    # path('projects/<int:course_id>/student/<str:registration_id>/', ProjectDetailView.as_view(), name='project-detail'),
    # path('courses/<int:course_id>/projects/<int:project_id>/students/', ProjectStudentListView.as_view(), name='project-student-list'),
    # path(
    #     'projects/<int:project_id>/courses/<int:course_id>/sessions/<int:session_id>/students/',
    #     ProjectStudentListView.as_view(),
    #     name='project-student-list'
    # ),
    path('projects/course/<int:course_id>/session/<int:session_id>/', ProjectsByCourseIDAPIView.as_view(), name='projects-by-course-id'),
    path('projects/<int:project_id>/courses/<int:course_id>/sessions/<int:session_id>/students/',ProjectStudentListView.as_view(),name='project-student-list'),
    path('projects/<int:course_id>/session/<int:session_id>/student/<str:registration_id>/',ProjectDetailView.as_view(), name='project-detail'),


    path('exams/', ExamListCreateAPIView.as_view(), name='exam-list-create'),
    path('exams/<int:pk>/', ExamDetailAPIView.as_view(), name='exam-detail'),
    path('exam_submissions/', ExamSubmissionListCreateAPIView.as_view(), name='exam-submission-list-create'),
    path('exam_submissions/<int:pk>/', ExamSubmissionDetailAPIView.as_view(), name='exam-submission-detail'),
    path('exam_gradings/', ExamGradingListCreateAPIView.as_view(), name='exam-grading-list-create'),
    path('exam_gradings/<int:pk>/', ExamGradingDetailAPIView.as_view(), name='exam-grading-detail'),

    # path('exams/course/<int:course_id>/', ExamsByCourseIDAPIView.as_view(), name='exams-by-course-id'),
    # path('exams/<int:course_id>/student/<str:registration_id>/', ExamDetailView.as_view(), name='exam-detail'),
    # path('courses/<int:course_id>/exams/<int:exam_id>/students/', ExamStudentListView.as_view(), name='exam-student-list'),
    # path('exams/<int:exam_id>/courses/<int:course_id>/sessions/<int:session_id>/students/',ExamStudentListView.as_view(),name='exam-student-list'),
    path('exams/course/<int:course_id>/session/<int:session_id>/', ExamsByCourseIDAPIView.as_view(), name='exams-by-course-id'),
    path('exams/<int:exam_id>/courses/<int:course_id>/sessions/<int:session_id>/students/',ExamStudentListView.as_view(),name='exam-student-list'),
    path('exams/<int:course_id>/session/<int:session_id>/student/<str:registration_id>/', ExamDetailView.as_view(), name='exam-detail'),
    
    path('courses/<int:course_id>/assignment-progress/', AssignmentProgressAPIView.as_view(), name='assignment-progress'),
    path('courses/<int:course_id>/quiz-progress/', QuizProgressAPIView.as_view(), name='quiz-progress'),
    path('course/<int:course_id>/course-progress/', CourseProgressAPIView.as_view(), name='course-progress'),
    path('weightages/', WeightageListCreateAPIView.as_view(), name='weightage-list-create'),
    path('weightages/<int:pk>/', WeightageDetailAPIView.as_view(), name='weightage-detail'),
    path('skills/', SkillListCreateAPIView.as_view(), name='skill-list-create'),
    path('skills/<int:pk>/', SkillRetrieveUpdateDestroyAPIView.as_view(), name='skill-detail'),
    path('course_weightages/<int:course_id>/session/<int:session_id>/', WeightageListByCourseId.as_view(), name='weightage-list-by-course'),
]
