"""changes"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    User, Specialization, Student, Board, 
    Card, SpeechSettings, AppSettings, Session, 
    DailyStreak, Feedback
)

User = get_user_model()

#1. AUTHENTICATION & PROFILE ---

class SpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialization
        fields = ['id', 'label']

class UserSerializer(serializers.ModelSerializer):
    initials = serializers.ReadOnlyField() 

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'password', 'initials',
            'first_name', 'last_name', 'display_name', 'contact_number', 
            'room_section', 'department', 'grade_handled', 'organization', 'bio'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

#2. STUDENT MANAGEMENT ---

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'


#3. COMMUNICATION BOARDS (Web + Mobile UI) ---

class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ['id', 'board', 'phrase', 'icon_url', 'order', 'created_at']

class BoardSerializer(serializers.ModelSerializer):
    # This nesting allows Mobile to get Cards inside the Board response
    cards = CardSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'educator', 'name', 'status', 'cards', 'created_at', 'updated_at']


#4. SPEECH & APP SETTINGS ---

class SpeechSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpeechSettings
        fields = '_all_'

class AppSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppSettings
        fields = '_all_'


#ANALYTICS (For Web StatCards & ActivityChart) ---

class SessionSerializer(serializers.ModelSerializer):
    duration_seconds = serializers.ReadOnlyField()

    class Meta:
        model = Session
        fields = ['id', 'student', 'started_at', 'ended_at', 'words_spoken', 'duration_seconds']

class DailyStreakSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyStreak
        fields = '_all_'


#FEEDBACK ---

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '_all_'