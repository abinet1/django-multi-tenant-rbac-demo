from rest_framework import permissions


class IsSuperadmin(permissions.BasePermission):
    """Allows access only to platform superadmin (no role, is_superuser=True)."""
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_superuser
            and not request.user.role
        )


class IsTenantAdmin(permissions.BasePermission):
    """Allows access to tenant-level admins."""
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'ADMIN'
        )


class IsManager(permissions.BasePermission):
    """Allows access to managers."""
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'MANAGER'
        )


class IsAdminOrManager(permissions.BasePermission):
    """Allows access to admins or managers."""
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ('ADMIN', 'MANAGER')
        )


class IsStaff(permissions.BasePermission):
    """Allows access to staff."""
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'STAFF'
        )


class IsCustomer(permissions.BasePermission):
    """Allows access to customers."""
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'CUSTOMER'
        )


class IsReadOnly(permissions.BasePermission):
    """Allows only safe HTTP methods (GET, HEAD, OPTIONS)."""
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsStaffInSameCompany(permissions.BasePermission):
    """Object-level: allows staff access only if object belongs to their company."""
    def has_object_permission(self, request, view, obj):
        if request.user.role != 'STAFF':
            return False
        return obj.company == request.user.company


class IsCustomerOwner(permissions.BasePermission):
    """Object-level: allows customer access only if they own the object."""
    def has_object_permission(self, request, view, obj):
        if request.user.role != 'CUSTOMER':
            return False
        return obj.customer == request.user
