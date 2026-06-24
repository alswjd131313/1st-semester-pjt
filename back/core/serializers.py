from rest_framework import serializers
from .models import (
    Material,
    MaterialSpec,
    RegulationMapping,
    Supplier,
    SupplyHistory,
    Demand,
    SupplierMaterialRegistration,
    SupplierInquiry,
    CommunityPost,
    CommunityComment,
    CommunityContactRequest,
)


class MaterialSpecSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialSpec
        exclude = ["id", "material"]


class RegulationMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegulationMapping
        exclude = ["id", "material"]


class MaterialListSerializer(serializers.ModelSerializer):
    """자재 목록용 (간략)"""
    category_display = serializers.CharField(source="get_category_display", read_only=True)

    class Meta:
        model = Material
        fields = [
            "id", "name", "ks_code", "ks_grade", "diameter",
            "category", "category_display", "material_group", "material_subtype",
            "is_seismic", "is_weldable",
        ]


class MaterialSuggestionSerializer(serializers.ModelSerializer):
    """메인 검색창 자동완성에 필요한 최소 자재 정보."""

    spec = serializers.SerializerMethodField()
    material_group = serializers.CharField(source="get_material_group_display", read_only=True)
    material_subtype = serializers.CharField(source="get_material_subtype_display", read_only=True)
    supplier_name = serializers.CharField(read_only=True, allow_null=True)
    available = serializers.BooleanField(read_only=True)

    class Meta:
        model = Material
        fields = [
            "id", "name", "spec", "material_group", "material_subtype",
            "supplier_name", "available",
        ]

    def get_spec(self, obj):
        return " ".join(part for part in (obj.ks_grade, obj.diameter) if part).strip()


class MaterialDetailSerializer(serializers.ModelSerializer):
    """자재 상세용 (물성치 + 규격 매핑 포함)"""
    spec       = MaterialSpecSerializer(read_only=True)
    regulation = RegulationMappingSerializer(read_only=True)
    category_display = serializers.CharField(source="get_category_display", read_only=True)

    class Meta:
        model = Material
        fields = [
            "id", "name", "ks_code", "ks_grade", "diameter",
            "category", "category_display", "material_group", "material_subtype",
            "is_seismic", "is_weldable",
            "spec", "regulation",
        ]


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = [
            "id", "name", "address", "phone",
            "latitude", "longitude", "source",
        ]


# ──────────────────────────────────────────
# 추천 결과 전용 시리얼라이저
# ──────────────────────────────────────────

class RecommendationSerializer(serializers.Serializer):
    """
    views.py에서 직접 dict를 조립해 넘기므로
    ModelSerializer 대신 Serializer를 사용한다.
    """

    rank     = serializers.IntegerField()
    supplier = SupplierSerializer()
    material = MaterialDetailSerializer()
    scores   = serializers.DictField()

    latest_unit_price  = serializers.DecimalField(max_digits=15, decimal_places=2, allow_null=True)
    supply_count       = serializers.IntegerField()
    category_experience_count = serializers.IntegerField(required=False, default=0)
    category_experience_score = serializers.IntegerField(required=False, default=0, min_value=0, max_value=5)
    distance_km        = serializers.FloatField(allow_null=True)
    route_distance_m   = serializers.IntegerField(allow_null=True, required=False)
    route_duration_sec = serializers.IntegerField(allow_null=True, required=False)
    route_status       = serializers.CharField(required=False)
    route_note         = serializers.CharField(required=False)
    approval_warning   = serializers.CharField(allow_null=True)
    data_source        = serializers.CharField(required=False, allow_blank=True)


class AlternativeResponseSerializer(serializers.Serializer):
    original_material = MaterialDetailSerializer()
    recommendations   = RecommendationSerializer(many=True)


# ──────────────────────────────────────────
# 단가 트렌드
# ──────────────────────────────────────────

class PriceTrendPointSerializer(serializers.Serializer):
    date        = serializers.DateField()
    avg_price   = serializers.DecimalField(max_digits=15, decimal_places=2)
    moving_avg  = serializers.DecimalField(max_digits=15, decimal_places=2)


class PriceTrendSerializer(serializers.Serializer):
    material_id = serializers.IntegerField()
    period      = serializers.CharField()
    data        = PriceTrendPointSerializer(many=True)
    insight     = serializers.CharField()


# ──────────────────────────────────────────
# 수요 등록
# ──────────────────────────────────────────

class DemandSerializer(serializers.ModelSerializer):
    material_name = serializers.CharField(source="material.__str__", read_only=True)
    owner_email = serializers.EmailField(source="owner.email", read_only=True)

    class Meta:
        model = Demand
        fields = [
            "id", "site_name", "site_lat", "site_lng",
            "owner_email",
            "material", "material_name",
            "quantity", "deadline", "memo", "created_at",
        ]
        read_only_fields = ["id", "created_at", "material_name", "owner_email"]


class SupplierMaterialRegistrationSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source="owner.email", read_only=True)
    owner_user_id = serializers.IntegerField(source="owner.id", read_only=True)

    class Meta:
        model = SupplierMaterialRegistration
        fields = [
            "id", "owner_email", "owner_user_id", "supplier_name", "contact", "address", "zip_no",
            "latitude", "longitude", "main_materials", "material_name", "standard",
            "strength_grade", "material_group", "specification", "ks_standard",
            "recent_price", "unit", "manufacturer", "stock_available", "service_area", "distance_km",
            "delivery_count", "note", "created_at",
        ]
        read_only_fields = ["id", "owner_email", "owner_user_id", "created_at"]


class SupplierInquirySerializer(serializers.ModelSerializer):
    requester_id = serializers.IntegerField(source="requester.id", read_only=True)
    requester_email = serializers.EmailField(source="requester.email", read_only=True)
    requester_company = serializers.SerializerMethodField()
    supplier_user_id = serializers.SerializerMethodField()
    supplier_email = serializers.SerializerMethodField()
    supplier_info = serializers.SerializerMethodField()

    class Meta:
        model = SupplierInquiry
        fields = [
            "id", "status", "created_at", "updated_at", "status_updated_at",
            "material_name", "standard", "quantity", "desired_date", "site_address",
            "requester_name", "contact", "message",
            "requester_id", "requester_email", "requester_company",
            "supplier_user_id", "supplier_email", "supplier_info",
        ]
        read_only_fields = [
            "id", "created_at", "updated_at",
            "requester_id", "requester_email", "requester_company",
            "supplier_user_id", "supplier_email", "supplier_info",
        ]

    def get_requester_company(self, obj):
        profile = getattr(obj.requester, "profile", None)
        return getattr(profile, "company_name", "") or ""

    def get_supplier_user_id(self, obj):
        return obj.supplier_user_id

    def get_supplier_email(self, obj):
        return obj.supplier_user.email if obj.supplier_user else None

    def get_supplier_info(self, obj):
        if not obj.supplier_user:
            return None
        profile = getattr(obj.supplier_user, "profile", None)
        company_name = getattr(profile, "company_name", "") or ""
        if not company_name:
            reg = obj.supplier_user.supplier_material_registrations.first()
            company_name = getattr(reg, "supplier_name", "") or ""
        return {
            "company_name": company_name,
        }


class SupplierInquiryStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierInquiry
        fields = ["status"]


def community_author_payload(user, anonymous=False, alias=""):
    if anonymous:
        return {
            "display_name": alias or "익명 사용자",
            "role": "익명 사용자",
            "affiliation": "",
            "avatar_text": "PF",
            "is_anonymous": True,
        }

    profile = getattr(user, "profile", None)
    role_labels = {"requester": "현장 자재 담당자", "supplier": "공급사 담당자"}
    name = user.first_name or user.username or "PaceFlow 사용자"
    return {
        "profile_id": user.id,
        "account_role": getattr(profile, "role", ""),
        "display_name": name,
        "role": role_labels.get(getattr(profile, "role", ""), "PaceFlow 사용자"),
        "affiliation": getattr(profile, "company_name", ""),
        "avatar_text": (name[:2] or "PF").upper(),
        "is_anonymous": False,
    }


class CommunityCommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = CommunityComment
        fields = ["id", "author", "display_mode", "content", "created_at", "is_owner"]
        read_only_fields = ["id", "author", "created_at", "is_owner"]

    def get_author(self, obj):
        return community_author_payload(
            obj.author,
            anonymous=obj.display_mode == "anonymous",
            alias=obj.anonymous_alias,
        )

    def get_is_owner(self, obj):
        request = self.context.get("request")
        return bool(request and request.user.is_authenticated and request.user == obj.author)


class CommunityPostSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    post_type_label = serializers.CharField(source="get_post_type_display", read_only=True)
    comment_count = serializers.IntegerField(read_only=True, default=0)
    comments = CommunityCommentSerializer(many=True, read_only=True)
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = CommunityPost
        fields = [
            "id", "author", "display_mode", "post_type", "post_type_label",
            "title", "content", "material_name", "supplier_name", "region",
            "status", "comment_count", "comments", "is_owner", "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "author", "comment_count", "comments", "is_owner", "created_at", "updated_at",
        ]

    def get_author(self, obj):
        return community_author_payload(
            obj.author,
            anonymous=obj.display_mode == "anonymous",
            alias=obj.anonymous_alias,
        )

    def get_is_owner(self, obj):
        request = self.context.get("request")
        return bool(request and request.user.is_authenticated and request.user == obj.author)


class CommunityContactRequestSerializer(serializers.ModelSerializer):
    post_title = serializers.CharField(source="post.title", read_only=True)
    target_display_name = serializers.SerializerMethodField()
    requester_display_name = serializers.SerializerMethodField()
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    direction = serializers.SerializerMethodField()

    class Meta:
        model = CommunityContactRequest
        fields = [
            "id", "post", "post_title", "target_display_name", "requester_display_name",
            "message", "status", "status_label", "direction", "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "post_title", "target_display_name", "requester_display_name",
            "status_label", "direction", "created_at", "updated_at",
        ]

    def get_target_display_name(self, obj):
        post = obj.post
        return community_author_payload(
            post.author,
            anonymous=post.display_mode == "anonymous",
            alias=post.anonymous_alias,
        )["display_name"]

    def get_requester_display_name(self, obj):
        return community_author_payload(obj.requester)["display_name"]

    def get_direction(self, obj):
        request = self.context.get("request")
        return "sent" if request and request.user == obj.requester else "received"
