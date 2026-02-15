from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id', 'tenant', 'company', 'created_by', 'customer',
            'name', 'description', 'share_token',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'tenant', 'company', 'created_by', 'customer',
            'share_token', 'created_at', 'updated_at',
        ]

    def create(self, validated_data):
        request = self.context['request']
        validated_data['tenant'] = request.user.tenant
        validated_data['company'] = request.user.company
        validated_data['created_by'] = request.user
        return super().create(validated_data)


class ProductClaimSerializer(serializers.Serializer):
    share_token = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate_share_token(self, value):
        try:
            product = Product.objects.get(share_token=value)
            if product.customer is not None:
                raise serializers.ValidationError("This product has already been claimed.")
            self.context['product'] = product
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("Invalid share token.")
