from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.throttling import UserRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken

from core.permissions import IsSuperadmin, IsTenantAdmin
from tenants.models import Tenant
from accounts.models import User
from .serializers import InvitationSerializer, InvitationAcceptSerializer


class BootstrapAdminInvitationView(APIView):
    """Superadmin only — creates a tenant-admin invitation with no tenant attached."""
    permission_classes = [IsSuperadmin]
    throttle_classes = [UserRateThrottle]

    def post(self, request):
        serializer = InvitationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            invitation = serializer.save(tenant=None, role='ADMIN')
            return Response(
                {"invitation_token": invitation.token},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ManagerInvitationView(APIView):
    """Admin only — creates a manager invitation scoped to the admin's tenant."""
    permission_classes = [IsTenantAdmin]
    throttle_classes = [UserRateThrottle]

    def post(self, request):
        serializer = InvitationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            invitation = serializer.save(role='MANAGER')
            return Response(
                {"invitation_token": invitation.token},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InvitationAcceptView(APIView):
    """Public — accepts any invitation token and returns JWT tokens."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = InvitationAcceptSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        invitation = serializer.validated_data['invitation']
        password = serializer.validated_data['password']

        if invitation.tenant is None:
            # Bootstrap: create Tenant + Admin user
            tenant = Tenant.objects.create(name=serializer.validated_data['tenant_name'])
            user = User.objects.create_user(
                email=invitation.email,
                password=password,
                role='ADMIN',
                tenant=tenant,
            )
        else:
            # Manager invite: user joins existing tenant
            user = User.objects.create_user(
                email=invitation.email,
                password=password,
                role='MANAGER',
                tenant=invitation.tenant,
            )

        invitation.used_at = timezone.now()
        invitation.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            "detail": "Accepted",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }, status=status.HTTP_200_OK)
