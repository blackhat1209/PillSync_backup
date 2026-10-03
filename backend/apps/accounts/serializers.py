from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "role", "phone"]
        read_only_fields = ["id", "role"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["username", "email", "password", "role", "phone", "first_name", "last_name"]
        extra_kwargs = {"role": {"required": False}}

    def validate_role(self, value):
        if value == User.Role.ADMIN:
            raise serializers.ValidationError("Admin accounts must be created by an administrator.")
        return value

    def create(self, validated_data):
        validated_data["role"] = validated_data.get("role") or User.Role.PATIENT
        return User.objects.create_user(**validated_data)


class PillSyncTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["username"] = user.username
        return token

    def validate(self, attrs):
        identifier = attrs.get(self.username_field)
        try:
            user = User.objects.get(email__iexact=identifier)
            attrs[self.username_field] = user.username
        except User.DoesNotExist:
            pass
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data
