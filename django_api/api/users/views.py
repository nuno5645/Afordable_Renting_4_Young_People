from django.shortcuts import render
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from .models import User, UserProfile
from .serializers import (
    UserSerializer, UserRegistrationSerializer, UserProfileSerializer,
    ChangePasswordSerializer, ResetPasswordEmailSerializer, ResetPasswordSerializer
)

# Create your views here.

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserRegistrationSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        profile_data = request.data
        profile = user.profile

        # Update profile fields if they exist in the request
        if 'price_range_min' in profile_data:
            profile.price_range_min = profile_data['price_range_min']
        if 'price_range_max' in profile_data:
            profile.price_range_max = profile_data['price_range_max']
        if 'min_bedrooms' in profile_data:
            profile.min_bedrooms = profile_data['min_bedrooms']
        if 'min_area' in profile_data:
            profile.min_area = profile_data['min_area']
        if 'notification_enabled' in profile_data:
            profile.notification_enabled = profile_data['notification_enabled']

        # Save the profile
        profile.save()

        # Return the updated user data
        serializer = self.get_serializer(user)
        return Response(serializer.data)

class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.data.get('old_password')):
            return Response({'old_password': ['Wrong password.']}, 
                          status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.data.get('new_password'))
        user.save()
        return Response({'message': 'Password updated successfully'}, 
                       status=status.HTTP_200_OK)

class RequestPasswordResetView(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email)
            token = get_random_string(length=32)
            user.set_password(token)
            user.save()

            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
            send_mail(
                'Password Reset Request',
                f'Click here to reset your password: {reset_url}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            return Response({'message': 'Password reset email has been sent.'}, 
                          status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'message': 'User with this email does not exist.'}, 
                          status=status.HTTP_404_NOT_FOUND)

class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            user = User.objects.get(password=serializer.validated_data['token'])
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': 'Password has been reset.'}, 
                          status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'message': 'Invalid token.'}, 
                          status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Successfully logged out.'}, 
                          status=status.HTTP_200_OK)
        except Exception:
            return Response({'message': 'Invalid token.'}, 
                          status=status.HTTP_400_BAD_REQUEST)
