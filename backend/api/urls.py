from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import (
    AIView,
    ApplicationView,
    AuthView,
    CompanyViewSet,
    JobViewSet,
    ResumeUploadView,
    SavedJobsView,
    SettingsView,
    UserViewSet,
)


router = SimpleRouter(trailing_slash=False)
router.trailing_slash = "/?"
router.register("jobs", JobViewSet, basename="job")
router.register("companies", CompanyViewSet, basename="company")
router.register("users", UserViewSet, basename="user")

urlpatterns = [
    path("auth/<str:action>", AuthView.as_view(), name="auth"),
    path("applications/", ApplicationView.as_view(), name="application-create"),
    path("applications/my", ApplicationView.as_view(), {"scope": "my"}, name="my-applications"),
    path("applications/admin", ApplicationView.as_view(), {"scope": "admin"}, name="admin-applications"),
    path(
        "applications/admin/<int:application_id>",
        ApplicationView.as_view(),
        name="admin-application-detail",
    ),
    path("saved-jobs/", SavedJobsView.as_view(), name="saved-jobs-create"),
    path("saved-jobs/my", SavedJobsView.as_view(), name="my-saved-jobs"),
    path("saved-jobs/<int:saved_id>", SavedJobsView.as_view(), name="saved-job-delete"),
    path("resume/upload", ResumeUploadView.as_view(), name="resume-upload"),
    path("ai/recommendations/", AIView.as_view(), {"action": "recommendations"}, name="ai-recommendations"),
    path("ai/job-matches/", AIView.as_view(), {"action": "job-matches"}, name="ai-job-matches"),
    path("ai/job-match/<int:job_id>", AIView.as_view(), {"action": "job-match"}, name="ai-job-match"),
    path("ai/resume/analyze", AIView.as_view(), {"action": "resume/analyze"}, name="ai-resume-analysis"),
    path("settings/", SettingsView.as_view(), name="settings"),
    path("settings/<str:action>", SettingsView.as_view(), name="settings-action"),
] + router.urls
