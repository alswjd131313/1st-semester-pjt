from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .serializers import LoginSerializer, ProfileUpdateSerializer, RegisterSerializer

ROLE_LABELS = {"requester": "자재 요청자", "supplier": "공급사"}


def _user_payload(user):
    profile = user.profile
    return {
        "id": user.id,
        "name": user.first_name,
        "email": user.email,
        "role": profile.role,
        "roleLabel": ROLE_LABELS[profile.role],
        "companyName": profile.company_name,
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
        {"token": token.key, "user": _user_payload(user)},
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
    return Response({"token": token.key, "user": _user_payload(user)})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    request.auth.delete()
    return Response({"message": "로그아웃 되었습니다."})


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def profile(request):
    user = request.user
    if request.method == "GET":
        return Response(_user_payload(user))

    serializer = ProfileUpdateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    name = data.get("name", "").strip()
    company_name = data.get("company_name", "").strip()
    current_pw = data.get("current_password", "").strip()
    new_pw = data.get("new_password", "").strip()

    if name:
        user.first_name = name
    if company_name:
        user.profile.company_name = company_name
        user.profile.save()

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
        return Response({"user": _user_payload(user), "token": token.key})

    user.save()
    return Response({"user": _user_payload(user)})
