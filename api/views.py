from rest_framework import viewsets, generics
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import MeSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User, StudentProfile, TeacherProfile, Board
from .serializers import (
    UserSerializer, 
    StudentProfileSerializer, 
    TeacherProfileSerializer, 
    BoardSerializer,
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
    MeSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class StudentProfileViewSet(viewsets.ModelViewSet):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer

class TeacherProfileViewSet(viewsets.ModelViewSet):
    queryset = TeacherProfile.objects.all()
    serializer_class = TeacherProfileSerializer

class BoardViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,) # This is crucial: it lets people hit this URL without being logged in yet!
    serializer_class = RegisterSerializer
    
class UserMeView(APIView):
    permission_classes = [IsAuthenticated] # Bouncer: Must be logged in!

    def get(self, request):
        # Read the profile
        serializer = MeSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        # Update the profile
        serializer = MeSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)