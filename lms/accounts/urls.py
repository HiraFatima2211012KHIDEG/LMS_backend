"""
Urls for the Accounts app
"""

from django.urls import path
from .views.application_views import *
from .views import user_views, UserSessionAPIView
from .views.location_views import *
from .views.attendance_views import *
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    # Admin
    path(
        "create-admin/", user_views.CreateAdminUserView.as_view(), name="create-admin"
    ),
    path(
        "admin-portal-count/",
        user_views.UsersCountAdminSectionView.as_view(),
        name="users-count",
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
    path(
        "application-count/<int:filteration_id>/",
        ApplicationStatusCount.as_view(),
        name="applications-count",
    ),
    path(
        "user-process/<int:filteration_id>/",
        user_views.ApplicationUserView.as_view(),
        name="application-user",
    ),


    # user creation and updation
    path("login/", user_views.UserLoginView.as_view(), name="login"),
    path("user-details/", UserSessionAPIView.as_view(), name="user-details"),
    path(
        "user-details/<int:user_id>/",
        user_views.UserDetailsView.as_view(),
        name="user-details",
    ),
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
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path(
        "user-profile-update/",
        user_views.UserProfileUpdateView.as_view(),
        name="user-profile-update",
    ),


    # Batch
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
        "users/filter-by-batch/<str:batch_id>/",
        FilterUsersByBatchView.as_view(),
        name="filter-users-by-batch",
    ),
    path("batch-student/", user_views.BatchStudentView.as_view(), name="batch-student"),


    # Session
    path("session/", SessionsAPIView.as_view(), name="sessions_list_create"),
    path("session/<int:pk>/", SessionsAPIView.as_view(), name="session_detail_update"),
    path(
        "sessions/calendar/<int:user_id>/",
        SessionCalendarAPIView.as_view(),
        name="session-list-calendar",
    ),
    path(
        "preferred-sessions/",
        user_views.PreferredSessionView.as_view(),
        name="preferred-sessions",
    ),
    path(
        "user-sessions/<int:user_id>/",
        user_views.UserSessionsView.as_view(),
        name="user-sessions",
    ),
    path(
        "sessions/<int:session_id>/students/",
        SessionsAPIViewAttendance.as_view(),
        name="session-students",
    ),
    # path(
    #     "filter-batches-by-city/",
    #     FilterBatchByCityView.as_view(),
    #     name="filter-batches-by-city",
    # ),
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


    # Student
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


    # Instructor
    path(
        "instructors", user_views.InstructorListView.as_view(), name="all-instructors"
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
        "instructor-preferred-sessions/",
        user_views.PreferredInstructorSessionView.as_view(),
        name="instructor-preferred-sessions",
    ),
    path(
        "instructor-sessions/",
        user_views.InstructorSessionsView.as_view(),
        name="instructor-sessions",
    ),
    path(
        "instructors/course/<int:course_id>/",
        InstructorsByCourseAPIView.as_view(),
        name="instructors-by-course",
    ),


    #Attendance
    path(
        "attendance/student/<int:course_id>/",
        StudentAttendanceListView.as_view(),
        name="student-attendance",
    ),
    path(
        "attendance/instructor/<int:session_id>/<int:course_id>/",
        InstructorAttendanceView.as_view(),
        name="instructor-attendance",
    ),
    path(
        "admin/attendance/<int:session_id>/",
        AdminAttendanceView.as_view(),
        name="admin-attendance",
    ),
    path("stats", BatchStatsView.as_view())
]
