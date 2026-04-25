from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db.models import Q
from .models import User, StudentProfile, TeacherProfile, Board

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Added your new custom fields so Django can send them to React!
        fields = ['id', 'username', 'email', 'full_name', 'status']

# NEW: The missing RegisterSerializer that handles Teacher signups!
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'full_name', 'status', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data.get('full_name', ''),
            status=validated_data.get('status', 'STUDENT')
        )
        return user

class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = '__all__'

class TeacherProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherProfile
        fields = '__all__'

class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = '__all__'
        
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    # 1. Define a generic text field so Django stops forcing strict "@email.com" formatting
    identifier = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Delete the default strict 'email' field that SimpleJWT tries to force
        if 'email' in self.fields:
            del self.fields['email']

    def validate(self, attrs):
        identifier = attrs.get('identifier')
        password = attrs.get('password')

        # 2. Search the database: Does the email match OR does the username match?
        try:
            user = User.objects.get(Q(email=identifier) | Q(username=identifier))
        except User.DoesNotExist:
            raise serializers.ValidationError('Invalid email/username or password.')

        # 3. Check the password
        if not user.check_password(password):
            raise serializers.ValidationError('Invalid email/username or password.')

        # 4. Generate the tokens and attach the Teacher Bouncer status
        self.user = user
        refresh = self.get_token(user)

        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'status': user.status, 
        }

        return data

class MeSerializer(serializers.ModelSerializer):
    # Pull these fields directly out of the connected TeacherProfile
    display_name   = serializers.CharField(source='teacher_profile.display_name', allow_blank=True, required=False)
    contact_number = serializers.CharField(source='teacher_profile.contact_number', allow_blank=True, required=False)
    room_section   = serializers.CharField(source='teacher_profile.room_section', allow_blank=True, required=False)
    department     = serializers.CharField(source='teacher_profile.department', allow_blank=True, required=False)
    grade_handled  = serializers.CharField(source='teacher_profile.grade_handled', allow_blank=True, required=False)
    organization   = serializers.CharField(source='teacher_profile.organization', allow_blank=True, required=False)
    bio            = serializers.CharField(source='teacher_profile.bio', allow_blank=True, required=False)
    
    # Catch first and last name from React so we can update the User's full_name
    first_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    last_name  = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ('email', 'full_name', 'first_name', 'last_name', 'display_name', 'contact_number', 
                  'room_section', 'department', 'grade_handled', 'organization', 'bio')
        read_only_fields = ('email',)

    def to_representation(self, instance):
        # When sending data TO React, split the full_name into first and last
        rep = super().to_representation(instance)
        parts = instance.full_name.split(' ') if instance.full_name else ['', '']
        rep['first_name'] = parts[0]
        rep['last_name'] = ' '.join(parts[1:]) if len(parts) > 1 else ''
        return rep

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('teacher_profile', {})
        
        # 1. Update the User's full_name if React sent changes
        first = validated_data.pop('first_name', None)
        last = validated_data.pop('last_name', None)
        if first is not None or last is not None:
            current_first = instance.full_name.split(' ')[0] if instance.full_name else ''
            current_last = ' '.join(instance.full_name.split(' ')[1:]) if instance.full_name else ''
            instance.full_name = f"{first if first is not None else current_first} {last if last is not None else current_last}".strip()
        instance.save()

        # 2. Update the TeacherProfile
        profile = instance.teacher_profile
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()

        return instance