from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("status", "TEACHER") # Make superusers teachers by default
        return self.create_user(email, username, password, **extra_fields)


# --- CORE AUTH USER ---
class User(AbstractBaseUser, PermissionsMixin):
    # 1. Define the status choices
    STATUS_CHOICES = (
        ('STUDENT', 'Student'),
        ('TEACHER', 'Teacher'),
    )

    username    = models.CharField(max_length=150, unique=True)
    email       = models.EmailField(unique=True)

    # 2. THE MISSING COLUMNS! This fixes your crash.
    full_name   = models.CharField(max_length=255, default="")
    status      = models.CharField(max_length=10, choices=STATUS_CHOICES, default='STUDENT')

    is_active   = models.BooleanField(default=True)
    is_staff    = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name        = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.full_name or self.username} <{self.email}>"


# --- PROFILES ---
class StudentProfile(models.Model):
    user         = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    name         = models.CharField(max_length=200)
    grade        = models.CharField(max_length=50)
    disabilities = models.TextField(blank=True, help_text="Details about specific disabilities or needs")

    def __str__(self):
        return f"Student: {self.name} (Grade {self.grade})"


class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="teacher_profile")
    
    # All the fields your Settings.tsx page expects!
    display_name   = models.CharField(max_length=200, blank=True, default="")
    contact_number = models.CharField(max_length=50, blank=True, default="")
    room_section   = models.CharField(max_length=100, blank=True, default="")
    department     = models.CharField(max_length=100, blank=True, default="")
    grade_handled  = models.CharField(max_length=100, blank=True, default="")
    organization   = models.CharField(max_length=255, blank=True, default="")
    bio            = models.TextField(blank=True, default="")

    def __str__(self):
        return f"Teacher: {self.display_name or self.user.full_name}"

# --- PLACEHOLDER ---
class Board(models.Model):
    teacher    = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name="boards")
    title      = models.CharField(max_length=150, default="Untitled Board")
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Add your specific card/communication logic here later

    def __str__(self):
        return self.title