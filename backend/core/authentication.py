from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.settings import api_settings
from django.utils.translation import gettext_lazy as _

class MongoUser:
    def __init__(self, user_id, email, role):
        self.id = user_id
        self.email = email
        self.role = role
        self.is_authenticated = True
        self.is_active = True

class MongoJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        """
        Attempts to find and return a user using the given validated token.
        Overrides the default Django ORM behavior to use our custom MongoUser object.
        """
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            raise AuthenticationFailed(_("Token contained no recognizable user identification"))

        # We can also extract other claims we stuffed into the token
        email = validated_token.get('email', '')
        role = validated_token.get('role', '')

        return MongoUser(user_id=user_id, email=email, role=role)
