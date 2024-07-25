"""
Urls for the Accounts app
"""
from django.urls import path
from .views.application_views import CreateApplicationView
from . views import user_views

urlpatterns = [
    path('applications', CreateApplicationView.as_view(), name='create-application'),
    path('create/', user_views.CreateUserView.as_view(), name='create'),
    path('login/', user_views.LoginView.as_view(), name='login'),
    path('logout/', user_views.LogoutView.as_view(), name='logout'),
]