from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

User = get_user_model()

class EmailOrUsernameModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # The Q object lets us do an "OR" search in the database
            # We check if the input matches EITHER the username OR the email
            user = User.objects.get(Q(username=username) | Q(email=username))
        except User.DoesNotExist:
            return None

        # If we found a user, check if the password matches
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
            
        return None