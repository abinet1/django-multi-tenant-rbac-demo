from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid
import secrets

INVITATION_ROLE_CHOICES = (
    ('ADMIN', 'Admin'),
    ('MANAGER', 'Manager'),
)


def generate_invitation_token():
    return secrets.token_urlsafe(48)


class Invitation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField()
    role = models.CharField(max_length=20, choices=INVITATION_ROLE_CHOICES)
    tenant = models.ForeignKey(
        'tenants.Tenant', on_delete=models.PROTECT, null=True, blank=True
    )
    token = models.CharField(
        max_length=64, unique=True, default=generate_invitation_token
    )
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_valid(self):
        if self.used_at:
            raise ValidationError('Invitation already used.')
        if timezone.now() > self.expires_at:
            raise ValidationError('Invitation expired.')
        return True

    def __str__(self):
        return f"Invitation for {self.email} ({self.role})"
