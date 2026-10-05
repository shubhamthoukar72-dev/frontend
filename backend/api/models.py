from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("An email address is required.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", User.Role.ADMIN)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("A superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("A superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        USER = "user", "User"
        ADMIN = "admin", "Admin"

    username = None
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.USER)
    phone = models.CharField(max_length=40, blank=True)
    location = models.CharField(max_length=160, blank=True)
    headline = models.CharField(max_length=200, blank=True)
    skills = models.TextField(blank=True)
    resume = models.FileField(upload_to="resumes/", blank=True)
    notifications_enabled = models.BooleanField(default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]
    objects = UserManager()

    def __str__(self):
        return self.email


class Company(models.Model):
    name = models.CharField(max_length=180, unique=True)
    industry = models.CharField(max_length=120, blank=True)
    location = models.CharField(max_length=180, blank=True)
    website = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Job(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "Active", "Active"
        CLOSED = "Closed", "Closed"
        DRAFT = "Draft", "Draft"

    title = models.CharField(max_length=180)
    company = models.CharField(max_length=180)
    location = models.CharField(max_length=180)
    job_type = models.CharField(max_length=80, blank=True)
    work_mode = models.CharField(max_length=80, blank=True)
    experience = models.CharField(max_length=100, blank=True)
    salary = models.CharField(max_length=120, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    created_by = models.ForeignKey(
        User, related_name="created_jobs", null=True, blank=True, on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} at {self.company}"


class Application(models.Model):
    class Status(models.TextChoices):
        PENDING = "Pending", "Pending"
        SHORTLISTED = "Shortlisted", "Shortlisted"
        INTERVIEW = "Interview", "Interview"
        HIRED = "Hired", "Hired"
        REJECTED = "Rejected", "Rejected"

    job = models.ForeignKey(Job, related_name="applications", on_delete=models.CASCADE)
    applicant = models.ForeignKey(User, related_name="applications", on_delete=models.CASCADE)
    cover_letter = models.TextField(blank=True)
    resume_url = models.CharField(max_length=500, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("job", "applicant"), name="unique_application_per_job_and_user"
            )
        ]


class SavedJob(models.Model):
    job = models.ForeignKey(Job, related_name="saved_by", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="saved_jobs", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("job", "user"), name="unique_saved_job_per_user")
        ]


class PlatformSettings(models.Model):
    site_name = models.CharField(max_length=120, default="Job Portal")
    support_email = models.EmailField(default="support@example.com")
    default_job_status = models.CharField(max_length=20, default=Job.Status.ACTIVE)
    allow_registration = models.BooleanField(default=True)
    maintenance_mode = models.BooleanField(default=False)
    notifications = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.site_name
