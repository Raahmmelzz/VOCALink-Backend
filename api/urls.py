from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, UserViewSet, BoardViewSet, CustomTokenObtainPairView, UserMeView
# Notice: CardViewSet has been removed from the import above!

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'boards', BoardViewSet, basename='board')
# Notice: The cards router line has been removed for now!

urlpatterns = [
    # Auth URLs
    path('auth/register/', RegisterView.as_view(), name='auth_register'),
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('users/me/', UserMeView.as_view(), name='user_me'),
    # Router URLs
    path('', include(router.urls)),
]