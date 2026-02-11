class TenantScopedMixin:
    """
    Mixin to scope querysets to the requesting user's tenant.
    Apply to any ModelViewSet that holds tenant-owned data.
    """
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_superuser:
            return queryset
        if user.tenant_id:
            return queryset.filter(tenant=user.tenant)
        return queryset.none()
