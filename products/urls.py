from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, ProductClaimView

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
    path('public/products/claim/', ProductClaimView.as_view(), name='product-claim'),
]
