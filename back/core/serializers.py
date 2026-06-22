from rest_framework import serializers
from .models import (
    Material,
    MaterialSpec,
    RegulationMapping,
    Supplier,
    SupplyHistory,
    Demand,
    SupplierMaterialRegistration,
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

    class Meta:
        model = SupplierMaterialRegistration
        fields = [
            "id", "owner_email", "supplier_name", "contact", "address", "zip_no",
            "latitude", "longitude", "main_materials", "material_name", "standard",
            "strength_grade", "recent_price", "service_area", "distance_km",
            "delivery_count", "note", "created_at",
        ]
        read_only_fields = ["id", "owner_email", "created_at"]
