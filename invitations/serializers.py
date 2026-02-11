from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from .models import Invitation, INVITATION_ROLE_CHOICES


class InvitationSerializer(serializers.ModelSerializer):
    expires_in_hours = serializers.IntegerField(write_only=True, required=False, default=48)

    class Meta:
        model = Invitation
        fields = [
            'id', 'email', 'role', 'tenant',
            'token', 'expires_at', 'used_at',
            'created_at', 'updated_at',
            'expires_in_hours',
        ]
        read_only_fields = ['id', 'token', 'expires_at', 'used_at', 'created_at', 'updated_at']

    def validate_role(self, value):
        valid_roles = [choice[0] for choice in INVITATION_ROLE_CHOICES]
        if value not in valid_roles:
            raise serializers.ValidationError("Invalid role. Must be ADMIN or MANAGER.")
        return value

    def create(self, validated_data):
        expires_in_hours = validated_data.pop('expires_in_hours', 48)
        validated_data['expires_at'] = timezone.now() + timedelta(hours=expires_in_hours)
        return super().create(validated_data)


class AcceptInvitationSerializer(serializers.Serializer):
    """Handles both bootstrap-admin and manager invitation acceptance."""
    token = serializers.CharField()
    password = serializers.CharField(write_only=True)
    tenant_name = serializers.CharField(required=False, allow_blank=True)
