from rest_framework import serializers
from django.utils import timezone
from django.core.exceptions import ValidationError as DjangoValidationError
from datetime import timedelta
from .models import Invitation, INVITATION_ROLE_CHOICES


class InvitationSerializer(serializers.ModelSerializer):
    expires_in_hours = serializers.IntegerField(write_only=True, required=False, default=48)
    # role is enforced by the view (ADMIN for bootstrap, MANAGER for admin invite)
    role = serializers.ChoiceField(choices=INVITATION_ROLE_CHOICES, required=False)

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

    def validate(self, data):
        # Auto-attach tenant from the requesting admin (for manager invites)
        request = self.context.get('request')
        if request and 'tenant' not in data and hasattr(request.user, 'tenant') and request.user.tenant:
            data['tenant'] = request.user.tenant
        return data

    def create(self, validated_data):
        expires_in_hours = validated_data.pop('expires_in_hours', 48)
        validated_data['expires_at'] = timezone.now() + timedelta(hours=expires_in_hours)
        return super().create(validated_data)


class InvitationAcceptSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    tenant_name = serializers.CharField(required=False)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        try:
            invitation = Invitation.objects.get(token=data['token'])
            invitation.is_valid()
            data['invitation'] = invitation

            if invitation.tenant is None:  # Bootstrap admin invite
                if not data.get('tenant_name'):
                    raise serializers.ValidationError(
                        {"tenant_name": "Required for bootstrap invitation."}
                    )
            else:  # Manager invite
                if data.get('tenant_name'):
                    raise serializers.ValidationError(
                        {"tenant_name": "Not allowed for manager invitation."}
                    )
        except Invitation.DoesNotExist:
            raise serializers.ValidationError({"token": "Invalid token."})
        except DjangoValidationError as e:
            raise serializers.ValidationError({"token": e.message})
        return data
