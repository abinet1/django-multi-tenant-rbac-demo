from rest_framework import serializers
from .models import Tenant, Company


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        # Reject name change on updates (PATCH/PUT)
        if self.instance and 'name' in data:
            raise serializers.ValidationError({
                "name": "Tenant name is read-only and cannot be changed."
            })
        return data


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'tenant', 'name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'tenant', 'created_at', 'updated_at']

    def validate(self, data):
        request = self.context.get('request')
        if request and hasattr(request.user, 'tenant') and request.user.tenant:
            data['tenant'] = request.user.tenant
        return data
