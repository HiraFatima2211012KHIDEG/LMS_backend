"""
Urls for the Accounts app
"""
from django.urls import path
from .views.application_views import *
from .views import user_views
from .views.location_views import (
    CityViewSet,
    BatchViewSet,
    LocationViewSet,
    SessionsViewSet,
    CreateBatchLocationSessionView,
    AssignSessionsView,
    FilterBatchByCityView,
    FilterLocationByCityView,
    # FilterSessionsByLocationView,
    # FilterSessionsView,
    CityStatsView,
    SessionCalendarAPIView

)
from .views.attendance_views import AttendanceDetailView,AttendanceFilterViewSet,AttendanceListCreateView,UserAttendanceListView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path(
        "create-admin/", user_views.CreateAdminUserView.as_view(), name="create-admin"
    ),
    # Applications
    path("applications/", CreateApplicationView.as_view(), name="create-application"),
    path(
        "applications-process/",
        ApplicationProcessView.as_view(),
        name="update-application",
    ),
    path(
        "applications-process/<int:filteration_id>/",
        ApplicationProcessView.as_view(),
        name="get-all-applications",
    ),
    # user creation and updation
    # path('registration/', UserRegistrationView.as_view(), name='registration-completion'),
    path("create/", user_views.CreateUserView.as_view(), name="create"),
    path("login/", user_views.UserLoginView.as_view(), name="login"),
    path(
        "change-password/",
        user_views.ChangePasswordView.as_view(),
        name="change-password",
    ),
    path(
        "reset-password-email/",
        user_views.ResetPasswordView.as_view(),
        name="reset-password-email",
    ),
    path(
        "reset-password/<uid>/<token>/",
        user_views.UserpasswordResetView.as_view(),
        name="reset-password",
    ),
    path("verify-email/", VerifyEmailandSetPasswordView.as_view(), name="verify-email"),
    path(
        "resend-verification-email/",
        ResendVerificationEmail.as_view(),
        name="resend-verification-email",
    ),
    path("user-profile/", user_views.UserProfileView.as_view(), name="user-profile"),
    # path('set-password/', user_views.SetPasswordView.as_view(), name='set-password'),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path(
        "user-profile-update/",
        user_views.UserProfileUpdateView.as_view(),
        name="user-profile-update",
    ),
    # user management
    path(
        "cities/",
        CityViewSet.as_view({"get": "list", "post": "create"}),
        name="city-list-create",
    ),
    path(
        "cities/<int:pk>/",
        CityViewSet.as_view({"get": "retrieve", "put": "update", "delete": "destroy"}),
        name="city-detail",
    ),
    path(
        "batch/",
        BatchViewSet.as_view({"get": "list", "post": "create"}),
        name="batch-list-create",
    ),
    path(
        "batch/<str:pk>/",
        BatchViewSet.as_view({"get": "retrieve", "put": "update", "delete": "destroy"}),
        name="batch-detail",
    ),
    path(
        "location/",
        LocationViewSet.as_view({"get": "list", "post": "create"}),
        name="location-list-create",
    ),
    path(
        "location/<int:pk>/",
        LocationViewSet.as_view(
            {"get": "retrieve", "put": "update", "delete": "destroy"}
        ),
        name="location-detail",
    ),
    path(
        "session/",
        SessionsViewSet.as_view({"get": "list", "post": "create"}),
        name="session-list-create",
    ),
    path(
        "session/<int:pk>/",
        SessionsViewSet.as_view(
            {"get": "retrieve", "put": "update", "delete": "destroy"}
        ),
        name="session-detail",
    ),
    path('sessions/calendar/<int:user_id>/', SessionCalendarAPIView.as_view(), name='session-list-calendar'),
    path(
        "filter-batches-by-city/",
        FilterBatchByCityView.as_view(),
        name="filter-batches-by-city",
    ),
    path(
        "filter-locations-by-city/",
        FilterLocationByCityView.as_view(),
        name="filter-locations-by-city",
    ),
    # path(
    #     "filter-sessions-by-location/",
    #     FilterSessionsByLocationView.as_view(),
    #     name="filter-sessions-by-location",
    # ),
    # path("filter-sessions/", FilterSessionsView.as_view(), name="filter-sessions"),
    path(
        "assign-session/<int:user_id>/<int:session_id>/",
        user_views.AssignSessionView.as_view(),
        name="assign-session",
    ),
    path("student/", user_views.CreateStudentView.as_view(), name="create-student"),
    path(
        "student/<str:registration_id>/",
        user_views.StudentDetailView.as_view(),
        name="detail-student",
    ),
    path(
        "course-students/",
        user_views.StudentFilterViewSet.as_view({"get": "list"}),
        name="course-students",
    ),
    path(
        "student-courses-instructors/<str:registration_id>/",
        user_views.StudentCoursesInstructorsView.as_view(),
        name="student_courses_instructors",
    ),
    path("students", user_views.StudentListView.as_view(), name="all-students"),
    path(
        "instructors", user_views.InstructorListView.as_view(), name="all-instructors"
    ),
    path(
        "instructors/<str:instructor_id>/assign-courses/",
        user_views.AssignCoursesView.as_view(),
        name="assign-courses",
    ),
    path(
        "instructor-courses/",
        user_views.InstructorCoursesViewSet.as_view({"get": "list"}),
        name="instructor-courses",
    ),
    path(
        "instructors/<str:instructor_id>/assign-sessions/",
        AssignSessionsView.as_view(),
        name="assign-sessions",
    ),
    path(
        "attendance/",
        AttendanceListCreateView.as_view({"get": "list", "post": "create"}),
        name="attendance-list-create",
    ),
    path(
        "attendance/<int:pk>/",
        AttendanceDetailView.as_view(
            {"get": "retrieve", "put": "update", "delete": "destroy"}
        ),
        name="attendance-detail",
    ),
    path(
        "attendance/course/<int:course_id>/user/<str:registration_id>/",
        UserAttendanceListView.as_view(),
        name="user-attendance-list",
    ),
    # path(
    #     "api/filter-attendance/",
    #     AttendanceFilterViewSet.as_view({"get": "list"}),
    #     name="filter-attendance",
    # ),
    path(
        "create-batch-location-session/",
        CreateBatchLocationSessionView.as_view(),
        name="create-batch-location-session",
    ),
    path(
        "techskills/",
        TechSkillViewSet.as_view({"get": "list", "post": "create"}),
        name="techskill-list-create",
    ),
    path(
        "techskills/<int:pk>/",
        TechSkillViewSet.as_view(
            {"get": "retrieve", "put": "update", "delete": "destroy"}
        ),
        name="techskill-detail",
    ),
    path(
        "application-count/<int:filteration_id>/",
        ApplicationStatusCount.as_view(),
        name="applications-count",
    ),
    path(
        "admin-portal-count/",
        user_views.UsersCountAdminSectionView.as_view(),
        name="users-count",
    ),
    path(
        "city-stats/",
        CityStatsView.as_view(),
        name="city-capacity-and-users",
    ),
    # path(
    #     "user-process/<int:filteration_id>/",
    #     user_views.UserProcessView.as_view(),
    #     name="users-count",
    # ),
    path('preferred-sessions/', user_views.PreferredSessionView.as_view(), name='preferred-sessions'),

    path('user-sessions/<int:user_id>/', user_views.UserSessionsView.as_view(), name='user-sessions'),
    path('instructor-sessions/', user_views.InstructorSessionsView.as_view(), name='instructor-sessions'),
    path('user-process/<int:filteration_id>/', user_views.ApplicationUserView.as_view(), name='application-user'),
    path('user-details/<int:user_id>/', user_views.UserDetailsView.as_view(), name='user-details'),
]
