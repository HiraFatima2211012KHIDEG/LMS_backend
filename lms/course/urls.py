from django.urls import path
from .views.views import *
from .views.content_view import *
from .views.assignment_view import *


urlpatterns = [
    path('programs/', ProgramListCreateAPIView.as_view(), name='program-list-create'),
    path('programs/<int:pk>/', ProgramDetailAPIView.as_view(), name='program-detail'),
    path('courses/', CourseListCreateAPIView.as_view(), name='course-list-create'),
    path('courses/<int:pk>/', CourseDetailAPIView.as_view(), name='course-detail'),
    path('modules/', ModuleListCreateAPIView.as_view(), name='module-list-create'),
    path('modules/<int:pk>/', ModuleDetailAPIView.as_view(), name='module-detail'),
    path('contents/', ContentListCreateAPIView.as_view(), name='content-list-create'),
    path('contents/<int:pk>/', ContentDetailAPIView.as_view(), name='content-detail'),
    path('toggle_active/<str:model_name>/<int:pk>/', ToggleActiveStatusAPIView.as_view(), name='toggle_active_status'),
    path('assignments/', AssignmentListCreateAPIView.as_view(), name='assignment-list-create'),
    path('assignments/<int:pk>/', AssignmentDetailAPIView.as_view(), name='assignment-detail'),
    path('submissions/', AssignmentSubmissionCreateAPIView.as_view(), name='submission-create'),
    path('submissions/<int:pk>/', AssignmentSubmissionDetailAPIView.as_view(), name='submission-detail'),
]
