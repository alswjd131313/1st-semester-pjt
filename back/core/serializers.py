from rest_framework import serializers
from .models import Material, MaterialSpec, RegulationMapping, Supplier, SupplyHistory, Demand


class MaterialSpecSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialSpec
        exclude = ["id", "material", "source"]


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
            "category", "category_display", "is_seismic", "is_weldable",
        ]


class MaterialDetailSerializer(serializers.ModelSerializer):
    """자재 상세용 (물성치 + 규격 매핑 포함)"""
    spec       = MaterialSpecSerializer(read_only=True)
    regulation = RegulationMappingSerializer(read_only=True)
    category_display = serializers.CharField(source="get_category_display", read_only=True)

    class Meta:
        model = Material
        fields = [
            "id", "name", "ks_code", "ks_grade", "diameter",
            "category", "category_display", "is_seismic", "is_weldable",
            "spec", "regulation",
        ]


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = [
            "id", "name", "address", "phone",
            "latitude", "longitude",
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
    distance_km        = serializers.FloatField()
    approval_warning   = serializers.CharField(allow_null=True)


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

    class Meta:
        model = Demand
        fields = [
            "id", "site_name", "site_lat", "site_lng",
            "material", "material_name",
            "quantity", "deadline", "memo", "created_at",
        ]
        read_only_fields = ["id", "created_at", "material_name"]