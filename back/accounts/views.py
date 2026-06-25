from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .serializers import LoginSerializer, ProfileUpdateSerializer, RegisterSerializer

ROLE_LABELS = {"requester": "자재 요청자", "supplier": "공급사"}


def _profile_image_url(user, request=None):
    image = getattr(user.profile, "profile_image", None)
    if not image:
        return ""
    try:
        url = image.url
    except ValueError:
        return ""
    return request.build_absolute_uri(url) if request else url


def _user_payload(user, request=None):
    profile = user.profile
    profile_image = _profile_image_url(user, request)
    default_site_latitude = profile.default_site_latitude
    default_site_longitude = profile.default_site_longitude
    return {
        "id": user.id,
        "name": user.first_name,
        "email": user.email,
        "role": profile.role,
        "roleLabel": ROLE_LABELS[profile.role],
        "companyName": profile.company_name,
        "company_name": profile.company_name,
        "profile_image": profile_image,
        "profileImage": profile_image,
        "defaultSiteAddress": profile.default_site_address,
        "defaultSiteDetailAddress": profile.default_site_detail_address,
        "defaultSiteZipNo": profile.default_site_zip_no,
        "defaultSiteLatitude": float(default_site_latitude) if default_site_latitude is not None else None,
        "defaultSiteLongitude": float(default_site_longitude) if default_site_longitude is not None else None,
        "default_site_address": profile.default_site_address,
        "default_site_detail_address": profile.default_site_detail_address,
        "default_site_zip_no": profile.default_site_zip_no,
        "default_site_latitude": float(default_site_latitude) if default_site_latitude is not None else None,
        "default_site_longitude": float(default_site_longitude) if default_site_longitude is not None else None,
    }


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = serializer.save()
    token, _ = Token.objects.get_or_create(user=user)
    return Response(
        {"token": token.key, "user": _user_payload(user, request)},
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data["email"]
    password = serializer.validated_data["password"]
    role = serializer.validated_data["role"]

    user = authenticate(request, username=email, password=password)
    if user is None:
        return Response(
            {"error": "이메일 또는 비밀번호가 올바르지 않습니다."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if not hasattr(user, "profile") or user.profile.role != role:
        return Response(
            {"error": "선택한 역할과 계정의 역할이 일치하지 않습니다."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key, "user": _user_payload(user, request)})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    request.auth.delete()
    return Response({"message": "로그아웃 되었습니다."})


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser, MultiPartParser, FormParser])
def profile(request):
    user = request.user
    if request.method == "GET":
        return Response(_user_payload(user, request))

    serializer = ProfileUpdateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    name = data.get("name", "").strip()
    company_name = data.get("company_name", "").strip()
    profile_image = data.get("profile_image")
    has_default_address = "default_site_address" in data
    has_default_detail_address = "default_site_detail_address" in data
    has_default_zip_no = "default_site_zip_no" in data
    has_default_latitude = "default_site_latitude" in data
    has_default_longitude = "default_site_longitude" in data
    current_pw = data.get("current_password", "").strip()
    new_pw = data.get("new_password", "").strip()

    if name:
        user.first_name = name
    if company_name:
        user.profile.company_name = company_name
    if profile_image:
        user.profile.profile_image = profile_image
    if user.profile.role == "requester":
        if has_default_address:
            user.profile.default_site_address = data.get("default_site_address", "").strip()
        if has_default_detail_address:
            user.profile.default_site_detail_address = data.get("default_site_detail_address", "").strip()
        if has_default_zip_no:
            user.profile.default_site_zip_no = data.get("default_site_zip_no", "").strip()
        if has_default_latitude:
            user.profile.default_site_latitude = data.get("default_site_latitude")
        if has_default_longitude:
            user.profile.default_site_longitude = data.get("default_site_longitude")
    if (
        company_name
        or profile_image
        or has_default_address
        or has_default_detail_address
        or has_default_zip_no
        or has_default_latitude
        or has_default_longitude
    ):
        user.profile.save()
        if company_name and user.profile.role == "supplier":
            from core.models import SupplierMaterialRegistration

            SupplierMaterialRegistration.objects.filter(owner=user).update(supplier_name=company_name)

    if new_pw:
        if not user.check_password(current_pw):
            return Response(
                {"current_password": "현재 비밀번호가 올바르지 않습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(new_pw)
        Token.objects.filter(user=user).delete()
        token, _ = Token.objects.get_or_create(user=user)
        user.save()
        return Response({"user": _user_payload(user, request), "token": token.key})

    user.save()
    return Response({"user": _user_payload(user, request)})
