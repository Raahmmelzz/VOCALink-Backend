from django.urls import path, include
from rest_framework.routers import DefaultRouter
<<<<<<< HEAD
=======
from rest_framework.authtoken.views import obtain_auth_token
>>>>>>> origin/nick-user2
from .views import UserViewSet, StudentViewSet, BoardViewSet, CardViewSet

# The router automatically creates the endpoints like /api/users/ and /api/students/
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'students', StudentViewSet)
router.register(r'boards', BoardViewSet)
router.register(r'cards', CardViewSet)

urlpatterns = [
    path('', include(router.urls)),
<<<<<<< HEAD
=======
    path('login/', obtain_auth_token, name='api_login'),
>>>>>>> origin/nick-user2
]