from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, ROLE_CHOICES


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'role', 'tenant', 'company',
            'is_active', 'is_staff', 'is_superuser',
            'created_at', 'updated_at', 'password',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_superuser']

    def validate_role(self, value):
        valid_roles = [choice[0] for choice in ROLE_CHOICES]
        if value not in valid_roles:
            raise serializers.ValidationError("Invalid role.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class StaffCreateSerializer(serializers.ModelSerializer):
    """Used by Admin/Manager to create staff directly with a password."""
    company_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'company_id', 'role', 'tenant', 'company']
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True},
            'role': {'read_only': True},
            'tenant': {'read_only': True},
            'company': {'read_only': True},
        }

    def validate_company_id(self, value):
        from tenants.models import Company
        request = self.context['request']
        try:
            company = Company.objects.get(id=value, tenant=request.user.tenant)
        except Company.DoesNotExist:
            raise serializers.ValidationError("Company not found in your tenant.")
        return company  # returns Company instance

    def create(self, validated_data):
        company = validated_data.pop('company_id')  # Company instance from validate_company_id
        password = validated_data.pop('password')
        request = self.context['request']
        user = User(
            email=validated_data['email'],
            role='STAFF',
            tenant=request.user.tenant,
            company=company,
        )
        user.set_password(password)
        user.save()
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': str(self.user.id),
            'email': self.user.email,
            'role': self.user.role,
        }
        return data
