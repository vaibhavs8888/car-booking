from django.contrib.auth.backends import ModelBackend
from register.models import registermodel

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = registermodel.objects.get(Email=username)
            if user.check_password(password):
                return user
        except registermodel.DoesNotExist:
            return None