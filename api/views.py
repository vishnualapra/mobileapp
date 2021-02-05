from django.shortcuts import render
from rest_framework.views import APIView
from . import models
from rest_framework.views import Response
# from . import serializer
from rest_framework import status
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
import random
import datetime
from django.core.mail import send_mail
from django.conf import settings 
from . import serializer
from rest_framework_simplejwt.views import TokenObtainPairView


# Create your views here.
def otp(id):
    profile = models.Profile.objects.get(user_id=id)
    otp_no = str(random.randint(100000,999999))
    profile.otp = otp_no
    now = datetime.datetime.now()
    now_plus_10 = now + datetime.timedelta(minutes = 10)
    profile.otp_expire = now_plus_10
    profile.otp_active = True
    profile.save()
    subject = 'OTP'
    message = f'Hi {profile.user.first_name}, OTP is {profile.otp}, valid till {profile.otp_expire}.' 
    email_from = settings.EMAIL_HOST_USER 
    recipient_list = [profile.user.email,]
    try:
        send_mail( subject, message, email_from, recipient_list ) 
    except Exception as e:
        print(str(e))
    return otp_no

    

class Register_View(APIView):

    def post(self,request):
        success = False
        try:
            name = request.data.get("name",None)
            email = request.data.get("email",None)
            mobile = request.data.get("mobile",None)
            if name and email and mobile:
                check_email = User.objects.filter(email=email).first()
                check_phone = models.Profile.objects.filter(mobile=mobile).first()
                if check_email:
                    stat = status.HTTP_400_BAD_REQUEST
                    data = {"message":"email already exist"}
                elif check_phone:
                    stat = status.HTTP_400_BAD_REQUEST
                    data = {"message":"number already exist"}
                else:
                    try:
                        user = User(first_name=name,email=email,username=mobile)
                        user.save()
                        profile = models.Profile()
                        profile.user = user
                        profile.mobile = mobile
                        profile.save()
                        stat = status.HTTP_200_OK
                        data = {"message":"success"}
                        success = True
                    except:
                        stat = status.HTTP_400_BAD_REQUEST
                        data = {"message":"enter valid data"}
            else:
                stat = status.HTTP_400_BAD_REQUEST
                data = {"message":"all fields required"}
            
        except:
            data = {"message":"error occured try again"}
            stat = status.HTTP_400_BAD_REQUEST
        return Response({'success':success,'data':data},status=stat)


class Login_View(APIView):
    def post(self,request):
        success = False
        try:
            login_type = request.data.get("type","email")
            loginid = request.data.get('user',None)
            if loginid:
                if login_type == "email":
                    user = User.objects.filter(email=loginid).first()
                else:
                    profile = models.Profile.objects.filter(mobile=loginid).first()
                    if profile:
                        user = profile.user
                    else:
                        user = None
                if user:
                    otpp = otp(user.id)
                    stat = status.HTTP_200_OK
                    success = True
                    data = {"message":"otp send to registerd email & mobile"}
                else:
                    stat = status.HTTP_400_BAD_REQUEST
                    data = {"message":"invalid user"}
            else:
                data = {"message":"user email/phone required"}
                stat = status.HTTP_400_BAD_REQUEST
        except Exception as e:
            data = {"message":"error occured try again"+str(e)}
            stat = status.HTTP_400_BAD_REQUEST
        return Response({'success':success,'data':data},status=stat)





class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = serializer.LoginSerializer



class GetProfile(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self,request):
        success = False
        try:
            profile = models.Profile.objects.get(user=request.user)
            ser = serializer.ProfileSerializer(profile,many=False)
            stat = status.HTTP_200_OK
            data = ser.data
            success = True
        except:
            data= {"message":"error"}
            stat = status.HTTP_400_BAD_REQUEST
        return Response({'success':success,'data':data},status=stat)


            
