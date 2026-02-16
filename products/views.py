from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken

from core.mixins import TenantScopedMixin
from core.permissions import IsStaff, IsStaffInSameCompany, IsCustomerOwner, IsAdminOrManager
from accounts.models import User
from .models import Product
from .serializers import ProductSerializer, ProductClaimSerializer


class ProductViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    # ====================== PERMISSIONS ======================
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update']:
            return [permissions.IsAuthenticated(), IsStaffInSameCompany()]
        return [permissions.IsAuthenticated()]

    # ====================== LIST FILTERING ======================
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if user.role == 'STAFF':
            return queryset.filter(company=user.company)          # own company only
        elif user.role == 'CUSTOMER':
            return queryset.filter(customer=user)                 # only claimed products
        elif user.role in ['ADMIN', 'MANAGER']:
            return queryset                                       # all in tenant (mixin already filters)
        return queryset.none()

    # ====================== DETAIL + OBJECT PERMISSIONS ======================
    def check_object_permissions(self, request, obj):
        user = request.user

        if user.role in ['ADMIN', 'MANAGER']:
            return  # tenant already scoped → full access

        elif user.role == 'STAFF':
            if not IsStaffInSameCompany().has_object_permission(request, self, obj):
                self.permission_denied(request, message="You can only access products in your company.")

        elif user.role == 'CUSTOMER':
            if not IsCustomerOwner().has_object_permission(request, self, obj):
                self.permission_denied(request, message="You can only access your own products.")

        super().check_object_permissions(request, obj)

    # ====================== CREATE ======================
    def perform_create(self, serializer):
        # Serializer already sets tenant, company, created_by (from Step 4)
        serializer.save()


class ProductClaimView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        serializer = ProductClaimSerializer(data=request.data, context={})
        if serializer.is_valid():
            product = serializer.context['product']
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            customer, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'role': 'CUSTOMER',
                    'tenant': product.tenant,
                    'is_active': True,
                    'password': User.objects.make_random_password(),
                }
            )
            
            if created:
                customer.set_password(password)
                customer.save()
            else:
                if customer.role != 'CUSTOMER':
                    return Response(
                        {"detail": "This email is already registered with a different role."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            product.customer = customer
            product.save()

            refresh = RefreshToken.for_user(customer)
            return Response({
                "detail": "Claimed",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
