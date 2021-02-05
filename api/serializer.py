import datetime 
import json
from rest_framework import exceptions
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from . import models
from rest_framework import serializers
from rest_framework import status
from django.utils import timezone
from django.contrib.auth.models import User


class LoginSerializer(TokenObtainPairSerializer):
    user = serializers.CharField(allow_blank=True)
    otp = serializers.CharField(allow_blank=True)
    login_type = serializers.CharField(allow_blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.fields['password']
        del self.fields["username"]

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['name'] = user.first_name
        return token

    def validate(self, attrs):
        user = attrs.get("user", None)
        otp = attrs.get("otp", None)
        login_type = attrs.get("login_type", "email")
        if login_type == "email":
            print(datetime.datetime.now())
            profile = models.Profile.objects.filter(user__email=user,otp=otp,otp_active=True).first()
        else:
            profile = models.Profile.objects.filter(mobile=user,otp=otp,otp_active=True).first()
        if profile:
            user = profile.user
            profile.otp_active = False
            profile.save()
            if profile.otp_expire < timezone.now():
                raise serializers.ValidationError(
                    detail="OTP expired.", code=status.HTTP_401_UNAUTHORIZED
                )
        else:
            user = None
        

        if user is None:
            raise serializers.ValidationError(
            detail="Invalid login.", code=status.HTTP_401_UNAUTHORIZED
        )

        if user.is_active:
            refresh = self.get_token(user)
            data = dict()
            data['refresh'] = str(refresh)
            data['access'] = str(refresh.access_token)
            return data

        if user.is_locked:
            raise serializers.ValidationError(
            detail="Account Locked. Contact Support.", code=status.HTTP_423_LOCKED
        )

        raise serializers.ValidationError(
            detail="User Account is Deactivated.", 
code=status.HTTP_401_UNAUTHORIZED
    )


class UserSer(serializers.ModelSerializer):
    class Meta:
        fields = ('first_name','email')
        model = User


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSer()
    class Meta:
        fields = ('mobile','user')
        model = models.Profile