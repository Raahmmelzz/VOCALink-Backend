<<<<<<< HEAD
=======
"""w/ user change"""
>>>>>>> origin/nick-user2
from rest_framework import viewsets
from .models import User, Student, Board, Card
from .serializers import (
    UserSerializer, StudentSerializer, BoardSerializer, 
    CardSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    def perform_create(self, serializer):
        serializer.save(educator=self.request.user)

class BoardViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer

    def perform_create(self, serializer):
        serializer.save(educator=self.request.user)

class CardViewSet(viewsets.ModelViewSet):
    queryset = Card.objects.all()
    serializer_class = CardSerializer