from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import uuid

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
