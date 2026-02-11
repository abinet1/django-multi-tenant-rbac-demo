from datetime import timedelta

from django.utils import timezone
from django.core.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
import secrets

from .serializers import CustomTokenObtainPairSerializer
from .models import User, ResetToken
from .throttles import LoginRateThrottle, PasswordResetRateThrottle


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    throttle_classes = [LoginRateThrottle]


class CustomTokenRefreshView(TokenRefreshView):
    throttle_classes = []


class PasswordResetRequestView(APIView):
    permission_classes = []
    throttle_classes = [PasswordResetRateThrottle]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response(
                {"detail": "Email is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(email=email).first()
        if user:
            reset_obj, created = ResetToken.objects.get_or_create(user=user)
            if not created:
                reset_obj.token = secrets.token_urlsafe(48)
                reset_obj.expires_at = timezone.now() + timedelta(hours=1)
                reset_obj.used_at = None
                reset_obj.save()
            token = reset_obj.token
        else:
            token = secrets.token_urlsafe(48)

        # Always identical message and status — no email existence leakage
        return Response({
            "detail": "If the email exists, a reset token has been generated.",
            "reset_token": token,
        }, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    permission_classes = []
    throttle_classes = []

    def post(self, request):
        reset_token_str = request.data.get('reset_token')
        new_password = request.data.get('new_password')
        if not reset_token_str or not new_password:
            return Response(
                {"detail": "reset_token and new_password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            reset_obj = ResetToken.objects.get(token=reset_token_str)
            reset_obj.is_valid()
            user = reset_obj.user
            user.set_password(new_password)
            user.save()
            reset_obj.used_at = timezone.now()
            reset_obj.save()
            return Response({"detail": "Password updated"}, status=status.HTTP_200_OK)
        except ResetToken.DoesNotExist:
            return Response(
                {"detail": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValidationError:
            return Response(
                {"detail": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
