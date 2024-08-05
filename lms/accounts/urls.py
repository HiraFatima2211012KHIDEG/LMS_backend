"""
Urls for the Accounts app
"""
from django.urls import path
from .views.application_views import CreateApplicationView, ApplicationProcessView, UserRegistrationView
from .views import user_views
from .views.location_views import (
    CityViewSet,
    BatchViewSet,
    LocationViewSet,
    SessionsViewSet,
    CreateStudentInstructorView,
    StudentInstructorDetailView
)
from rest_framework_simplejwt.views import  TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('applications/', CreateApplicationView.as_view(), name='create-application'),
    path('applications-process/<int:application_id>/', ApplicationProcessView.as_view(), name='update-application'),
    path('applications-process/', ApplicationProcessView.as_view(), name='get-all-applications'),
    path('registration/', UserRegistrationView.as_view(), name='registration-completion'),
    path('create/', user_views.CreateUserView.as_view(), name='create'),
    path('login/', user_views.UserLoginView.as_view(), name='login'),
    path('change-password/', user_views.ChangePasswordView.as_view(), name='change-password'),
    path('reset-password-email/', user_views.ResetPasswordView.as_view(), name='reset-password-email'),
    path('reset-password/<uid>/<token>/', user_views.UserpasswordResetView.as_view(), name='reset-password'),
    path('user-profile/', user_views.UserProfileView.as_view(), name='user-profile'),
    path('set-password/', user_views.SetPasswordView.as_view(), name='set-password'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user-profile-update/', user_views.UserProfileUpdateView.as_view(), name='user-profile-update'),
    path('cities/', CityViewSet.as_view({'get': 'list', 'post': 'create'}), name='city-list-create'),
    path('cities/<int:pk>/', CityViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='city-detail'),
    path('batch/', BatchViewSet.as_view({'get': 'list', 'post': 'create'}), name='batch-list-create'),
    path('batch/<int:pk>/', BatchViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='batch-detail'),
    path('location/', LocationViewSet.as_view({'get': 'list', 'post': 'create'}), name='location-list-create'),
    path('location/<int:pk>/', LocationViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='location-detail'),
    path('session/', SessionsViewSet.as_view({'get': 'list', 'post': 'create'}), name='session-list-create'),
    path('session/<int:pk>/', SessionsViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='session-detail'),
    path('student-instructor/', CreateStudentInstructorView.as_view(), name='create-student-instructor'),
    path('student-instructor/<str:registration_id>/', StudentInstructorDetailView.as_view(), name='detail-student-instructor'),

]
