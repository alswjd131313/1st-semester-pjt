from django.contrib.auth.models import User
from rest_framework import serializers

from .models import UserProfile


class RegisterSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=["requester", "supplier"])
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6, write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    company_name = serializers.CharField(max_length=100)

    def validate_email(self, value):
        normalized = value.strip().lower()
        if User.objects.filter(email=normalized).exists():
            raise serializers.ValidationError("이미 사용 중인 이메일입니다.")
        return normalized

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "비밀번호가 일치하지 않습니다."})
        return data

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        role = validated_data.pop("role")
        name = validated_data.pop("name")
        company_name = validated_data.pop("company_name")
        email = validated_data["email"]
        password = validated_data.pop("password")

        user = User.objects.create_user(
            username=email,
            email=email,
            first_name=name,
            password=password,
        )
        UserProfile.objects.create(user=user, role=role, company_name=company_name)
        return user


class LoginSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=["requester", "supplier"])
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
