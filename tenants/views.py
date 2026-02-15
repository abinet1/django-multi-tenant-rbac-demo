from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated

from core.mixins import TenantScopedMixin
from core.permissions import IsAdminOrManager, IsTenantAdmin
from .models import Company
from .serializers import TenantSerializer, CompanySerializer


class TenantMeView(generics.RetrieveUpdateAPIView):
    serializer_class = TenantSerializer
    permission_classes = [IsAuthenticated, IsAdminOrManager]

    def get_object(self):
        print("TenantMeView.get_object called for user:", self.request.user.__dict__)
        return self.request.user.tenant

    def get_permissions(self):
        if self.request.method in ('PATCH', 'PUT'):
            return [IsAuthenticated(), IsTenantAdmin()]
        return super().get_permissions()

    def perform_update(self, serializer):
        # Belt-and-suspenders: strip name even if serializer.validate() missed it
        serializer.validated_data.pop('name', None)
        serializer.save()


class CompanyViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    http_method_names = ['get', 'post', 'patch', 'head', 'options']

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.tenant)
