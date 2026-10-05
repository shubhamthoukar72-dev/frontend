from pathlib import Path

from django.conf import settings
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.files.storage import default_storage
from django.db.models import Q
from django.shortcuts import get_object_or_404
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .ai import (
    AIServiceError,
    analyze_job_match,
    analyze_resume,
    chat_with_ai,
    extract_resume_text,
    recommend_jobs,
)
from .models import Application, Company, Job, PlatformSettings, SavedJob, User
from .permissions import IsAdminRole, ReadOnlyOrAdmin
from .serializers import (
    ApplicationSerializer,
    CompanySerializer,
    JobSerializer,
    PlatformSettingsSerializer,
    RegisterSerializer,
    SavedJobSerializer,
    UserSerializer,
)


def token_response(user):
    return {
        "access_token": str(RefreshToken.for_user(user).access_token),
        "user": UserSerializer(user).data,
    }


class AuthView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, action):
        if action == "register":
            if not PlatformSettings.objects.first() or PlatformSettings.objects.first().allow_registration:
                serializer = RegisterSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                return Response(token_response(serializer.save()), status=status.HTTP_201_CREATED)
            return Response({"detail": "Registration is currently disabled."}, status=403)

        if action == "login":
            email = str(request.data.get("email", "")).strip().lower()
            password = request.data.get("password", "")
            user = authenticate(request, email=email, password=password)
            if user is None or not user.is_active:
                return Response({"detail": "Invalid email or password."}, status=401)
            return Response(token_response(user))

        if action == "google":
            if not settings.GOOGLE_CLIENT_ID:
                return Response({"detail": "Google sign-in is not configured."}, status=503)
            credential = request.data.get("credential")
            if not credential:
                return Response({"detail": "A Google credential is required."}, status=400)
            try:
                payload = id_token.verify_oauth2_token(
                    credential, google_requests.Request(), settings.GOOGLE_CLIENT_ID
                )
            except ValueError:
                return Response({"detail": "The Google credential is invalid or expired."}, status=401)
            email = payload.get("email", "").strip().lower()
            if not email or not payload.get("email_verified"):
                return Response({"detail": "Google did not verify this email address."}, status=401)
            user = User.objects.filter(email=email).first()
            if user is None:
                return Response(
                    {"detail": "This Google account has not been provisioned as an administrator."},
                    status=403,
                )
            if user.role != User.Role.ADMIN and not user.is_staff:
                return Response({"detail": "This account is not permitted to sign in as an admin."}, status=403)
            return Response(token_response(user))

        return Response({"detail": "Unsupported authentication action."}, status=404)


class JobViewSet(viewsets.ModelViewSet):
    serializer_class = JobSerializer
    queryset = Job.objects.all().order_by("-created_at")
    permission_classes = [ReadOnlyOrAdmin]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not IsAdminRole().has_permission(self.request, self):
            queryset = queryset.filter(status=Job.Status.ACTIVE)
        query = self.request.query_params.get("search")
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query)
                | Q(company__icontains=query)
                | Q(location__icontains=query)
                | Q(description__icontains=query)
            )
        return queryset

    def perform_create(self, serializer):
        settings_object = PlatformSettings.objects.first()
        if "status" not in serializer.validated_data and settings_object:
            serializer.save(
                created_by=self.request.user,
                status=settings_object.default_job_status,
            )
            return
        serializer.save(created_by=self.request.user)


class CompanyViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer
    queryset = Company.objects.all().order_by("name")
    permission_classes = [ReadOnlyOrAdmin]

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.query_params.get("search")
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query)
                | Q(industry__icontains=query)
                | Q(location__icontains=query)
            )
        return queryset


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all().order_by("-date_joined")
    permission_classes = [IsAdminRole]
    http_method_names = ["get", "put", "patch", "delete", "head", "options"]


class ApplicationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, scope):
        if scope == "my":
            applications = Application.objects.filter(applicant=request.user).select_related("job")
        elif scope == "admin":
            if not IsAdminRole().has_permission(request, self):
                return Response({"detail": "Admin access is required."}, status=403)
            applications = Application.objects.select_related("job", "applicant").all()
        else:
            return Response({"detail": "Unknown application collection."}, status=404)
        return Response(ApplicationSerializer(applications.order_by("-created_at"), many=True).data)

    def post(self, request):
        payload = request.data.copy()
        payload["job"] = request.data.get("job_id", request.data.get("job"))
        payload["resume_url"] = (
            request.data.get("resume_url")
            or (request.user.resume.url if request.user.resume else "")
        )
        serializer = ApplicationSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        job = serializer.validated_data["job"]
        if job.status != Job.Status.ACTIVE:
            return Response({"detail": "This job is not accepting applications."}, status=400)
        if Application.objects.filter(job=job, applicant=request.user).exists():
            return Response({"detail": "You have already applied for this job."}, status=400)
        application = serializer.save(applicant=request.user)
        return Response(ApplicationSerializer(application).data, status=status.HTTP_201_CREATED)

    def _update_admin_application(self, request, application_id):
        if not IsAdminRole().has_permission(request, self):
            return Response({"detail": "Admin access is required."}, status=403)
        application = get_object_or_404(Application, pk=application_id)
        status_value = request.data.get("status")
        valid_statuses = {value for value, _label in Application.Status.choices}
        if status_value not in valid_statuses:
            raise ValidationError({"status": "Choose a valid application status."})
        application.status = status_value
        application.save(update_fields=["status"])
        return Response(ApplicationSerializer(application).data)

    def put(self, request, application_id=None):
        return self._update_admin_application(request, application_id)

    def patch(self, request, application_id=None):
        return self._update_admin_application(request, application_id)

    def delete(self, request, application_id=None):
        if not IsAdminRole().has_permission(request, self):
            return Response({"detail": "Admin access is required."}, status=403)
        application = get_object_or_404(Application, pk=application_id)
        application.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SavedJobsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        saved_jobs = SavedJob.objects.filter(user=request.user).select_related("job").order_by("-created_at")
        return Response(SavedJobSerializer(saved_jobs, many=True).data)

    def post(self, request):
        job = get_object_or_404(Job, pk=request.data.get("job_id"))
        saved, _created = SavedJob.objects.get_or_create(user=request.user, job=job)
        return Response(SavedJobSerializer(saved).data, status=status.HTTP_201_CREATED)

    def delete(self, request, saved_id=None):
        saved_job = get_object_or_404(SavedJob, pk=saved_id, user=request.user)
        saved_job.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ResumeUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        uploaded_file = request.FILES.get("file")
        if uploaded_file is None:
            return Response({"detail": "Choose a resume file to upload."}, status=400)
        extension = Path(uploaded_file.name).suffix.lower()
        if extension not in {".pdf", ".doc", ".docx"}:
            return Response({"detail": "Only PDF, DOC and DOCX files are allowed."}, status=400)
        if uploaded_file.size > 5 * 1024 * 1024:
            return Response({"detail": "Resume must be smaller than 5 MB."}, status=400)
        stored_path = default_storage.save(f"resumes/{uploaded_file.name}", uploaded_file)
        request.user.resume = stored_path
        request.user.save(update_fields=["resume"])
        resume_url = request.build_absolute_uri(settings.MEDIA_URL + stored_path)
        return Response(
            {"filename": Path(uploaded_file.name).name, "resume_url": resume_url, "url": resume_url},
            status=status.HTTP_201_CREATED,
        )


class AIView(APIView):
    permission_classes = [IsAuthenticated]

    def _handle_ai(self, operation):
        try:
            return Response(operation())
        except AIServiceError as error:
            return Response({"detail": error.detail}, status=error.status_code)

    def _resume_text(self, request):
        if not request.user.resume:
            raise AIServiceError(
                "Upload a PDF or DOCX resume before requesting AI analysis.",
                status_code=400,
            )
        return extract_resume_text(request.user.resume)

    def get(self, request, action, job_id=None):
        if action == "recommendations":
            def get_recommendations():
                resume_text = self._resume_text(request)
                jobs = list(
                    Job.objects.filter(status=Job.Status.ACTIVE)
                    .order_by("-created_at")
                    .values(
                        "id",
                        "title",
                        "company",
                        "location",
                        "job_type",
                        "work_mode",
                        "experience",
                        "salary",
                        "description",
                    )[:30]
                )
                return {
                    "recommendations": recommend_jobs(resume_text, jobs),
                    "filename": Path(request.user.resume.name).name,
                }

            return self._handle_ai(get_recommendations)

        if action == "job-matches":
            def get_job_matches():
                resume_text = self._resume_text(request)
                jobs = list(
                    Job.objects.filter(status=Job.Status.ACTIVE)
                    .order_by("-created_at")
                    .values(
                        "id",
                        "title",
                        "company",
                        "location",
                        "job_type",
                        "work_mode",
                        "experience",
                        "salary",
                        "description",
                    )[:30]
                )
                recommendations = recommend_jobs(resume_text, jobs)
                return {
                    "matches": [
                        {
                            "job_id": item["id"],
                            "match": {
                                "match_score": item["match_score"],
                                "matched_skills": item["matched_skills"],
                                "missing_skills": item["missing_skills"],
                                "fit_summary": item["fit_summary"],
                            },
                        }
                        for item in recommendations
                    ]
                }

            return self._handle_ai(get_job_matches)

        if action == "job-match" and job_id is not None:
            def get_job_match():
                job = get_object_or_404(Job, pk=job_id, status=Job.Status.ACTIVE)
                job_data = {
                    "title": job.title,
                    "company": job.company,
                    "location": job.location,
                    "job_type": job.job_type,
                    "work_mode": job.work_mode,
                    "experience": job.experience,
                    "description": job.description,
                }
                return {
                    "match": analyze_job_match(self._resume_text(request), job_data)
                }

            return self._handle_ai(get_job_match)

        if action == "resume/analyze":
            def get_resume_analysis():
                resume_text = self._resume_text(request)
                return {
                    "filename": Path(request.user.resume.name).name,
                    "analysis": analyze_resume(resume_text),
                }

            return self._handle_ai(get_resume_analysis)

        return Response({"detail": "Unknown AI endpoint."}, status=404)

    def post(self, request, action):
        if action != "resume/analyze":
            return Response({"detail": "Unknown AI endpoint."}, status=404)
        return self.get(request, action)


class ChatView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "ai_chat"

    def post(self, request):
        messages = request.data.get("messages")
        if not isinstance(messages, list) or not 1 <= len(messages) <= 12:
            return Response(
                {"detail": "Send between 1 and 12 chat messages."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        validated_messages = []
        total_characters = 0
        for message in messages:
            if not isinstance(message, dict) or message.get("role") not in {"user", "assistant"}:
                return Response(
                    {"detail": "Each message must have a user or assistant role."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            content = message.get("content")
            if not isinstance(content, str) or not content.strip() or len(content) > 2000:
                return Response(
                    {"detail": "Each message must contain 1 to 2000 characters."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            total_characters += len(content)
            if total_characters > 8000:
                return Response(
                    {"detail": "The conversation is too long. Start a new chat."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            validated_messages.append(
                {"role": message["role"], "content": content.strip()}
            )

        if validated_messages[-1]["role"] != "user":
            return Response(
                {"detail": "The last chat message must be from the user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            return Response({"reply": chat_with_ai(validated_messages)})
        except AIServiceError as error:
            return Response({"detail": error.detail}, status=error.status_code)


class SettingsView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request, action=""):
        settings_object, _created = PlatformSettings.objects.get_or_create(pk=1)
        return Response(
            {
                "profile": {
                    "name": request.user.name,
                    "email": request.user.email,
                    "phone": request.user.phone,
                },
                "notifications": {
                    "newApplications": True,
                    "newUsers": True,
                    "jobUpdates": True,
                    "emailNotifications": True,
                    **settings_object.notifications,
                },
                "platform": {
                    "platformName": settings_object.site_name,
                    "supportEmail": settings_object.support_email,
                    "defaultJobStatus": settings_object.default_job_status,
                    "maintenanceMode": settings_object.maintenance_mode,
                },
            }
        )

    def put(self, request, action=""):
        settings_object, _created = PlatformSettings.objects.get_or_create(pk=1)
        if action == "profile":
            email = str(request.data.get("email", request.user.email)).strip().lower()
            if User.objects.exclude(pk=request.user.pk).filter(email=email).exists():
                return Response({"detail": "That email address is already in use."}, status=400)
            request.user.name = request.data.get("name", request.user.name)
            request.user.email = email
            request.user.phone = request.data.get("phone", request.user.phone)
            request.user.save(update_fields=["name", "email", "phone"])
            return Response(
                {"name": request.user.name, "email": request.user.email, "phone": request.user.phone}
            )
        if action == "password":
            old_password = request.data.get("current_password", "")
            new_password = request.data.get("new_password", "")
            if not request.user.check_password(old_password):
                return Response({"detail": "Current password is incorrect."}, status=400)
            try:
                from django.contrib.auth.password_validation import validate_password

                validate_password(new_password, request.user)
            except DjangoValidationError as error:
                return Response({"detail": " ".join(error.messages)}, status=400)
            request.user.set_password(new_password)
            request.user.save(update_fields=["password"])
            return Response({"detail": "Password updated."})
        if action == "notifications":
            settings_object.notifications = {
                key: bool(request.data.get(key, False))
                for key in ("newApplications", "newUsers", "jobUpdates", "emailNotifications")
            }
            settings_object.save(update_fields=["notifications", "updated_at"])
            return Response({"notifications": settings_object.notifications})
        if action == "platform":
            settings_object.site_name = request.data.get("platformName", settings_object.site_name)
            settings_object.support_email = request.data.get(
                "supportEmail", settings_object.support_email
            )
            settings_object.default_job_status = request.data.get(
                "defaultJobStatus", settings_object.default_job_status
            )
            settings_object.maintenance_mode = bool(
                request.data.get("maintenanceMode", settings_object.maintenance_mode)
            )
            settings_object.save()
            return Response(
                {
                    "platformName": settings_object.site_name,
                    "supportEmail": settings_object.support_email,
                    "defaultJobStatus": settings_object.default_job_status,
                    "maintenanceMode": settings_object.maintenance_mode,
                }
            )
        serializer = PlatformSettingsSerializer(
            settings_object, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request, action=""):
        return self.put(request, action)
