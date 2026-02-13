from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TenantMeView, CompanyViewSet

router = DefaultRouter()
router.register(r'companies', CompanyViewSet, basename='company')

urlpatterns = [
    path('tenant/me/', TenantMeView.as_view(), name='tenant-me'),
    path('', include(router.urls)),
]
