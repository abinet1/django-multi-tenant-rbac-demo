from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
import uuid
import secrets

ROLE_CHOICES = (
    ('ADMIN', 'Admin'),
    ('MANAGER', 'Manager'),
    ('STAFF', 'Staff'),
    ('CUSTOMER', 'Customer'),
)


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, null=True, blank=True)
    tenant = models.ForeignKey(
        'tenants.Tenant', on_delete=models.PROTECT, null=True, blank=True
    )
    company = models.ForeignKey(
        'tenants.Company', on_delete=models.PROTECT, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def clean(self):
        super().clean()
        if self.role == 'STAFF' and not self.company_id:
            raise ValidationError(_('Staff must have a company assigned.'))
        if self.role in ('ADMIN', 'MANAGER', 'CUSTOMER') and self.company_id:
            raise ValidationError(_('Admins, Managers, and Customers cannot have a company assigned.'))
        if not self.is_superuser and not self.tenant_id:
            raise ValidationError(_('Non-superadmin users must belong to a tenant.'))
        if self.company_id and self.tenant_id and self.tenant_id != self.company.tenant_id:
            raise ValidationError(_('Company tenant must match user tenant.'))

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'accounts_user'


def generate_reset_token():
    return secrets.token_urlsafe(48)


def reset_token_expiry():
    return timezone.now() + timedelta(hours=1)


class ResetToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='reset_token')
    token = models.CharField(max_length=64, unique=True, default=generate_reset_token)
    expires_at = models.DateTimeField(default=reset_token_expiry)
    used_at = models.DateTimeField(null=True, blank=True)

    def is_valid(self):
        if self.used_at:
            raise ValidationError('Token already used.')
        if timezone.now() > self.expires_at:
            raise ValidationError('Token expired.')
        return True
