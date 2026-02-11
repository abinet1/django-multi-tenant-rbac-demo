from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),
    path('api/', include('tenants.urls')),
    path('api/', include('invitations.urls')),
    path('api/', include('products.urls')),
]
