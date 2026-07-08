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
    default_site_address = serializers.CharField(required=False, allow_blank=True)
    default_site_detail_address = serializers.CharField(max_length=200, required=False, allow_blank=True)
    default_site_zip_no = serializers.CharField(max_length=10, required=False, allow_blank=True)
    default_site_latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    default_site_longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)

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
        default_site_address = validated_data.pop("default_site_address", "")
        default_site_detail_address = validated_data.pop("default_site_detail_address", "")
        default_site_zip_no = validated_data.pop("default_site_zip_no", "")
        default_site_latitude = validated_data.pop("default_site_latitude", None)
        default_site_longitude = validated_data.pop("default_site_longitude", None)
        email = validated_data["email"]
        password = validated_data.pop("password")

        user = User.objects.create_user(
            username=email,
            email=email,
            first_name=name,
            password=password,
        )
        UserProfile.objects.create(
            user=user,
            role=role,
            company_name=company_name,
            default_site_address=default_site_address if role == "requester" else "",
            default_site_detail_address=default_site_detail_address if role == "requester" else "",
            default_site_zip_no=default_site_zip_no if role == "requester" else "",
            default_site_latitude=default_site_latitude if role == "requester" else None,
            default_site_longitude=default_site_longitude if role == "requester" else None,
        )
        return user


class LoginSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=["requester", "supplier"])
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class ProfileUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100, required=False)
    company_name = serializers.CharField(max_length=100, required=False)
    profile_image = serializers.FileField(required=False, allow_empty_file=False)
    default_site_address = serializers.CharField(required=False, allow_blank=True)
    default_site_detail_address = serializers.CharField(max_length=200, required=False, allow_blank=True)
    default_site_zip_no = serializers.CharField(max_length=10, required=False, allow_blank=True)
    default_site_latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    default_site_longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    current_password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    new_password = serializers.CharField(min_length=6, write_only=True, required=False, allow_blank=True)

    def validate(self, data):
        new_pw = data.get("new_password", "").strip()
        current_pw = data.get("current_password", "").strip()
        if new_pw and not current_pw:
            raise serializers.ValidationError({"current_password": "현재 비밀번호를 입력해 주세요."})
        return data
