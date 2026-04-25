from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, TeacherProfile, StudentProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    # This runs the exact millisecond a new User is inserted into the database
    if created:
        if instance.status == 'TEACHER':
            TeacherProfile.objects.create(
                user=instance,
                name=instance.full_name,
                specialty="General",
                organization="VocaLink"
            )
        elif instance.status == 'STUDENT':
            StudentProfile.objects.create(
                user=instance,
                name=instance.full_name,
                grade="Not Assigned"
            )