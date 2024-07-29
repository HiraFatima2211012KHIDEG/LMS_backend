"""
Urls for the Accounts app
"""
from django.urls import path
from .views.application_views import CreateApplicationView
from . views import user_views
from rest_framework_simplejwt.views import  TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('applications', CreateApplicationView.as_view(), name='create-application'),
    path('create/', user_views.CreateUserView.as_view(), name='create'),
    path('login/', user_views.UserLoginView.as_view(), name='login'),
    path('change-password/', user_views.ChangePasswordView.as_view(), name='change-password'),
    path('reset-password-email/', user_views.ResetPasswordView.as_view(), name='reset-password-email'),
    path('reset-password/<uid>/<token>/', user_views.UserpasswordResetView.as_view(), name='reset-password'),
    path('user-profile/', user_views.UserProfileView.as_view(), name='user-profile'),
    path('set-password/', user_views.SetPasswordView.as_view(), name='set-password'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # path('logout/', user_views.LogoutView.as_view(), name='logout'),
]