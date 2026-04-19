from django.contrib import admin
from .models import (
    User, 
    Specialization, 
    Student, 
    Board, 
    Card, 
    SpeechSettings, 
    SpeechContext, 
    AppSettings, 
    Session, 
    DailyStreak, 
    Feedback
)

# Register your models here so they appear in the Django admin panel
admin.site.register(User)
admin.site.register(Specialization)
admin.site.register(Student)
admin.site.register(Board)
admin.site.register(Card)
admin.site.register(SpeechSettings)
admin.site.register(SpeechContext)
admin.site.register(AppSettings)
admin.site.register(Session)
admin.site.register(DailyStreak)
admin.site.register(Feedback)