from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView
from django.contrib.auth.decorators import login_required
from . import views, forms

urlpatterns = [
    # Setup nginx to serve favicon https://simpleit.rocks/python/django/django-favicon-adding/
    path(
        "favicon.ico",
        RedirectView.as_view(url=staticfiles_storage.url("favicon.ico")),
    ),
    path("", views.index, name="index"),
    path("about/", views.about, name="about"),
    path("courses/", views.CourseList.as_view(), name="courses"),
    path("courses/<int:pk>/", views.CourseDetailView.as_view(), name="course-detail"),
    path(
        "my-courses/",
        login_required(views.MyCourseList.as_view(), login_url="/login"),
        name="my-courses",
    ),
    path("unit/<int:unit_id>/step/<int:step_id>/", views.lesson, name="lesson"),
    path("course-ended/<int:course_id>/", views.course_ended, name="course-ended"),
    path("tests/<int:test_id>/", views.get_test),
    path("save-test/", views.save_test),
    path(
        "delete-attendance/<int:course_id>/",
        views.delete_attendance,
        name="delete-attendance",
    ),
    path("get-passed-percentage/", views.get_passed_percentage),
    path("login/", views.login_user, name="login"),
    path("register/", views.register_user, name="register"),
    path(
        "registration-continued/",
        views.registration_continued,
        name="register_continue",
    ),
    path("logout/", views.logout_user, name="logout"),
    path("password_reset/", views.password_reset_request, name="password_reset"),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="myapp/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="myapp/password_reset_confirm.html",
            form_class=forms.MySetPasswordForm,
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="myapp/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("profile/", views.profile, name="profile"),
]
