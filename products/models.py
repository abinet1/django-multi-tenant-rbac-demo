from django.db import models
from django.core.exceptions import ValidationError
import uuid
import secrets


def generate_share_token():
    return secrets.token_urlsafe(48)


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.PROTECT)
    company = models.ForeignKey('tenants.Company', on_delete=models.PROTECT)
    created_by = models.ForeignKey(
        'accounts.User', on_delete=models.PROTECT, related_name='created_products'
    )
    customer = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='claimed_products'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    share_token = models.CharField(
        max_length=64, unique=True, default=generate_share_token
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        if self.created_by_id and self.created_by.role != 'STAFF':
            raise ValidationError('Products can only be created by Staff.')
        if self.created_by_id and self.tenant_id != self.created_by.tenant_id:
            raise ValidationError("Product tenant must match creator's tenant.")
        if self.created_by_id and self.company_id != self.created_by.company_id:
            raise ValidationError("Product company must match creator's company.")
        if self.customer_id and self.customer.role != 'CUSTOMER':
            raise ValidationError('Customer must have CUSTOMER role.')
        if self.customer_id and self.tenant_id != self.customer.tenant_id:
            raise ValidationError('Customer tenant must match product tenant.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
