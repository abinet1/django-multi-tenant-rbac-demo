from django.urls import path
from .views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    StaffListCreateView,
    AdminCustomerListView,
    AdminCustomerProductsView,
)

urlpatterns = [
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('auth/password-reset/request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('auth/password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('staff/', StaffListCreateView.as_view(), name='staff-list-create'),
    path('admin/customers/', AdminCustomerListView.as_view(), name='admin-customers'),
    path('admin/customers/<uuid:customer_id>/products/', AdminCustomerProductsView.as_view(), name='admin-customer-products'),
]
