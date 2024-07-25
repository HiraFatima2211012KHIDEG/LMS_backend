from django.urls import path
from .views.views import *


urlpatterns = [
    path('programs/', ProgramListCreateAPIView.as_view(), name='program-list-create'),
    path('programs/<int:pk>/', ProgramDetailAPIView.as_view(), name='program-detail'),
    path('courses/', CourseListCreateAPIView.as_view(), name='course-list-create'),
    path('courses/<int:pk>/', CourseDetailAPIView.as_view(), name='course-detail'),
    path('modules/', ModuleListCreateAPIView.as_view(), name='module-list-create'),
    path('modules/<int:pk>/', ModuleDetailAPIView.as_view(), name='module-detail'),
    path('toggle_active/<str:model_name>/<int:pk>/', ToggleActiveStatusAPIView.as_view(), name='toggle_active_status'),
]
