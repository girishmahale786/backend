from dj_rest_auth.serializers import (
    LoginSerializer,
    UserDetailsSerializer,
    PasswordResetSerializer,
)
from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework.validators import UniqueValidator
from allauth.account.utils import user_pk_to_url_str
from rest_framework import serializers, exceptions
from accounts.models import User
from django.conf import settings


def url_generator(request, user, temp_key):
    url = settings.FRONTEND_PASSWORD_RESET_URL
    url = url.replace("{uid}", user_pk_to_url_str(user))
    url = url.replace("{token}", temp_key)
    return url


class RegisterSerializer(RegisterSerializer):
    username = None
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    email = serializers.EmailField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )

    def custom_signup(self, request, user):
        first_name = self.validated_data.get("first_name", "")
        last_name = self.validated_data.get("last_name", "")
        user.first_name = first_name
        user.last_name = last_name
        user.save()


class LoginSerializer(LoginSerializer):
    username = None
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        try:
            return super().validate(attrs)
        except serializers.ValidationError as e:
            raise exceptions.AuthenticationFailed(str(e.detail[0]))


class UserDetailsSerializer(UserDetailsSerializer):
    class Meta(UserDetailsSerializer.Meta):
        fields = ("id", "email", "first_name", "last_name")


class PasswordResetSerializer(PasswordResetSerializer):

    def get_email_options(self):
        return {
            "url_generator": url_generator,
        }
