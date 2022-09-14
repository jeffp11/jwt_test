from importlib.metadata import requires
from rest_framework import exceptions, serializers
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken 
from django.contrib.auth.models import update_last_login
from django.contrib.auth import authenticate
from django.conf import settings
import jwt, uuid


class TokenPairSerializer(TokenObtainSerializer):
    token_class = RefreshToken

    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)

        data["access_token"] = str(refresh.access_token)
        data["refresh_token"] = str(refresh)

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        token['user'] = user.username
        token['tenant_id'] = 2
        
        return token


class TokenRefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()
    access_token = serializers.CharField(read_only=True)
    token_class = RefreshToken

    def validate(self, attrs):
        refresh = self.token_class(attrs["refresh_token"])

        data = {"access_token": str(refresh.access_token)}

        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    refresh.blacklist()
                except AttributeError:
                    pass

            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()

            data["refresh_token"] = str(refresh)

        return data
    

class ApplicationSerializer(serializers.Serializer):
    app = serializers.CharField(required=True)
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
     
    def validate(self, attrs):
        authenticate_kwargs = {
            "username": attrs["username"],
            "password": attrs["password"],
        }

        self.user = authenticate(**authenticate_kwargs)
        if not api_settings.USER_AUTHENTICATION_RULE(self.user):
            raise exceptions.AuthenticationFailed(
                self.error_messages["no_active_account"],
                "no_active_account",
            )
        
        if self.user.is_authenticated and self.user.is_superuser:
            uid = str(uuid.uuid1())
            a1 = {"app": self.initial_data.get('app'), "uid": uid}
            a2 = {"username": self.initial_data.get('username'), "uid": uid}
            return {
                "cliend_id": jwt.encode(a1, "key", algorithm="HS512"),
                "client_secret": jwt.encode(a2, "key", algorithm="HS512")
            }
        return {}
        