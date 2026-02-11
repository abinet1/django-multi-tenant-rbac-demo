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


class PublicProductClaimSerializer(serializers.Serializer):
    """Used by the public claim endpoint — no auth required."""
    share_token = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
