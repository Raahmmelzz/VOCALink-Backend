from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, TeacherProfile, StudentProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.status == 'TEACHER':
            TeacherProfile.objects.create(
                user=instance,
                display_name=instance.full_name, # Changed from 'name'
                department="General",            # Changed from 'specialty'
                organization="VocaLink"
            )
        elif instance.status == 'STUDENT':
            StudentProfile.objects.create(
                user=instance,
                name=instance.full_name,
                grade="Not Assigned"
            )