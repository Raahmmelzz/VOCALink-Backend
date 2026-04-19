"""test changes"""
from django.db import models

# Create your models here.



from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


#  USER / AUTH
#    Covers: login, signup, profile edit, password change, forgot password,
#            specializations, organization, bio (Web + Mobile)

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
        return self.create_user(email, username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    
    # Core identity
    username        = models.CharField(max_length=150, unique=True)
    email           = models.EmailField(unique=True)

    # Web educator profile
    organization    = models.CharField(max_length=255, blank=True)
    bio             = models.TextField(blank=True)

    # Mobile profile
    display_name    = models.CharField(max_length=150, blank=True,
                                       help_text="Shown in mobile Settings header")

    # Django internals
    is_active       = models.BooleanField(default=True)
    is_staff        = models.BooleanField(default=False)
    date_joined     = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name        = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.username} <{self.email}>"

    @property
    def initials(self):
        """Derived field used by both Web and Mobile avatars."""
        name = self.display_name or self.username
        parts = name.split()
        return "".join(p[0] for p in parts[:2]).upper()


class Specialization(models.Model):
    user  = models.ForeignKey(User, on_delete=models.CASCADE, related_name="specializations")
    label = models.CharField(max_length=100)

    class Meta:
        unique_together = ("user", "label")

    def __str__(self):
        return f"{self.user.username} — {self.label}"



# STUDENT MANAGEMENT
#    Covers: Web → Manage Students (add / edit / remove student profiles)

class Student(models.Model):
    educator  = models.ForeignKey(User, on_delete=models.CASCADE, related_name="students",
                                  help_text="The educator who owns this student profile")
    name      = models.CharField(max_length=200)
    grade     = models.CharField(max_length=50)
    need      = models.CharField(max_length=200, verbose_name="Special Need")
    address   = models.TextField()
    guardian  = models.CharField(max_length=200)
    contact   = models.CharField(max_length=11, help_text="Philippine mobile number, 11 digits")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} (Grade {self.grade})"


# 
# COMMUNICATION BOARDS & CARDS
#    Covers:
#      Web   → BoardConfig (add / rename / toggle active / remove boards)
#      Mobile → Communication Cards (categories with phrases / icons)

class Board(models.Model):

    class Status(models.TextChoices):
        ACTIVE   = "Active",   "Active"
        INACTIVE = "Inactive", "Inactive"

    educator   = models.ForeignKey(User, on_delete=models.CASCADE, related_name="boards")
    name       = models.CharField(max_length=150)
    status     = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering            = ["name"]
        unique_together     = ("educator", "name")

    def __str__(self):
        return f"{self.name} ({self.status})"


class Card(models.Model):
    board      = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="cards")
    phrase     = models.CharField(max_length=500, help_text="Text displayed and spoken via TTS")
    icon_url   = models.URLField(blank=True, help_text="Optional icon/image for the card")
    order      = models.PositiveIntegerField(default=0, help_text="Display order within the board")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "phrase"]

    def __str__(self):
        return f'"{self.phrase}" [{self.board.name}]'



# SPEECH / TTS SETTINGS
#    Covers:
#      Web    = Speech Contexts page (TTS configuration per educator)
#      Mobile = Settings → Communication → Speech Settings (rate, pitch, language)
#               Settings → Communication → Sound / Vibration / Haptic / Auto-Save toggles

class SpeechSettings(models.Model):

    class SpeechRate(models.TextChoices):
        SLOW   = "Slow",   "Slow"
        NORMAL = "Normal", "Normal"
        FAST   = "Fast",   "Fast"

    class Pitch(models.TextChoices):
        LOW    = "Low",    "Low"
        MEDIUM = "Medium", "Medium"
        HIGH   = "High",   "High"

    LANGUAGE_CHOICES = [
        ("en", "English"),
        ("fil", "Filipino"),
        ("es", "Spanish"),
        ("fr", "French"),
        ("ja", "Japanese"),
        ("ko", "Korean"),
        ("zh", "Mandarin"),
    ]

    user             = models.OneToOneField(User, on_delete=models.CASCADE,
                                            related_name="speech_settings")

    # TTS engine settings
    language         = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default="en")
    speech_rate      = models.CharField(max_length=10, choices=SpeechRate.choices,
                                        default=SpeechRate.NORMAL)
    pitch            = models.CharField(max_length=10, choices=Pitch.choices,
                                        default=Pitch.MEDIUM)

    # Mobile toggle preferences (Settings → Communication)
    sound_enabled    = models.BooleanField(default=True,  help_text="Play audio cues")
    vibration        = models.BooleanField(default=False, help_text="Haptic on card tap")
    haptic_feedback  = models.BooleanField(default=True,  help_text="Tactile response on actions")
    auto_save_cards  = models.BooleanField(default=True,  help_text="Save new phrases automatically")

    updated_at       = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} — Speech Settings"


class SpeechContext(models.Model):
    educator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="speech_contexts")
    phrase   = models.CharField(max_length=500)
    boost    = models.IntegerField(default=10,
                                   help_text="Confidence boost for this phrase in TTS recognition (1-20)")
    note     = models.CharField(max_length=255, blank=True,
                                help_text="Optional label, e.g. 'student name' or 'location'")

    def __str__(self):
        return f'"{self.phrase}" (boost: {self.boost})'



# APPEARANCE / APP SETTINGS
#    Covers: Mobile → Settings → Appearance (dark mode, large text, high contrast)
#            Mobile → Settings → Notifications (push notifications toggle)

class AppSettings(models.Model):
    user               = models.OneToOneField(User, on_delete=models.CASCADE,
                                              related_name="app_settings")

    # Appearance
    dark_mode          = models.BooleanField(default=False)
    large_text         = models.BooleanField(default=False)
    high_contrast      = models.BooleanField(default=False)

    # Notifications
    push_notifications = models.BooleanField(default=True)

    updated_at         = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} — App Settings"



# ACTIVITY / SESSION TRACKING
#    Covers: Web Dashboard → StatCards, ActivityChart, TopStudentsTable
#    Tracks student app usage so the educator dashboard can display:
#      - Total/active students, words spoken, streaks
#      - Weekly/monthly activity charts

class Session(models.Model):
    student      = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="sessions")
    started_at   = models.DateTimeField(default=timezone.now)
    ended_at     = models.DateTimeField(null=True, blank=True)
    words_spoken = models.PositiveIntegerField(default=0,
                                               help_text="Number of card phrases spoken during this session")

    @property
    def duration_seconds(self):
        if self.ended_at:
            return (self.ended_at - self.started_at).seconds
        return None

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.student.name} session @ {self.started_at:%Y-%m-%d %H:%M}"


class DailyStreak(models.Model):
    student        = models.OneToOneField(Student, on_delete=models.CASCADE,
                                          related_name="streak")
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_active    = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.name} — streak: {self.current_streak}d"



# FEEDBACK
#    Covers: Mobile → Settings → About → Send Feedback

class Feedback(models.Model):
    user       = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="feedbacks")
    message    = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.user or 'anonymous'} @ {self.submitted_at:%Y-%m-%d}"