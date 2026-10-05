from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Application, Company, Job, PlatformSettings, SavedJob, User


class JobNameField(serializers.PrimaryKeyRelatedField):
    def use_pk_only_optimization(self):
        return False

    def to_representation(self, value):
        return value.title


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "name",
            "email",
            "role",
            "phone",
            "location",
            "headline",
            "skills",
            "notifications_enabled",
            "date_joined",
            "is_active",
        )
        read_only_fields = ("id", "date_joined")


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ("name", "email", "password", "role")

    def validate_email(self, value):
        return value.strip().lower()

    def create(self, validated_data):
        validated_data.pop("role", None)
        return User.objects.create_user(**validated_data, role=User.Role.USER)


class CompanySerializer(serializers.ModelSerializer):
    jobs = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = ("id", "name", "industry", "location", "website", "description", "jobs")

    def get_jobs(self, company):
        return Job.objects.filter(company__iexact=company.name).count()


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = (
            "id",
            "title",
            "company",
            "location",
            "job_type",
            "work_mode",
            "experience",
            "salary",
            "description",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class ApplicationSerializer(serializers.ModelSerializer):
    job = JobNameField(queryset=Job.objects.all())
    job_id = serializers.IntegerField(source="job.id", read_only=True)
    company = serializers.CharField(source="job.company", read_only=True)
    applicant = serializers.CharField(source="applicant.name", read_only=True)
    applicant_id = serializers.IntegerField(source="applicant.id", read_only=True)
    email = serializers.EmailField(source="applicant.email", read_only=True)
    applied_at = serializers.DateTimeField(source="created_at", read_only=True)
    appliedOn = serializers.DateTimeField(source="created_at", read_only=True)

    class Meta:
        model = Application
        fields = (
            "id",
            "job",
            "job_id",
            "company",
            "applicant",
            "applicant_id",
            "email",
            "cover_letter",
            "resume_url",
            "status",
            "created_at",
            "applied_at",
            "appliedOn",
        )
        read_only_fields = ("id", "applicant", "status", "created_at")


class SavedJobSerializer(serializers.ModelSerializer):
    saved_id = serializers.IntegerField(source="id", read_only=True)
    job_id = serializers.IntegerField(source="job.id", read_only=True)
    saved_at = serializers.DateTimeField(source="created_at", read_only=True)

    class Meta:
        model = SavedJob
        fields = ("id", "saved_id", "job", "job_id", "saved_at", "created_at")
        read_only_fields = fields


class PlatformSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatformSettings
        fields = (
            "site_name",
            "support_email",
            "default_job_status",
            "allow_registration",
            "maintenance_mode",
            "notifications",
            "updated_at",
        )
        read_only_fields = ("updated_at",)
