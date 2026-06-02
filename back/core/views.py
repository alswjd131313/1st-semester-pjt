import math
from decimal import Decimal
from datetime import date, timedelta
from collections import defaultdict

from django.db.models import Avg, Count, Max, Min
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Material, MaterialSpec, Supplier, SupplyHistory, Demand
from .serializers import (
    MaterialListSerializer,
    MaterialDetailSerializer,
    AlternativeResponseSerializer,
    PriceTrendSerializer,
    DemandSerializer,
)


# ══════════════════════════════════════════
# 유틸: 거리 계산 (Haversine)
# ══════════════════════════════════════════

def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    두 좌표 사이 거리를 km 단위로 반환한다.
    """
    R = 6371
    d_lat = math.radians(float(lat2) - float(lat1))
    d_lng = math.radians(float(lng2) - float(lng1))
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(float(lat1)))
        * math.cos(math.radians(float(lat2)))
        * math.sin(d_lng / 2) ** 2
    )
    return R * 2 * math.asin(math.sqrt(a))


# ══════════════════════════════════════════
# 유틸: 이동평균 계산
# ══════════════════════════════════════════

def moving_average(data: list[dict], window: int = 3) -> list[dict]:
    """
    월별 평균 단가 리스트에 이동평균(window=3)을 추가해 반환한다.
    """
    result = []
    for i, point in enumerate(data):
        start = max(0, i - window + 1)
        window_prices = [d["avg_price"] for d in data[start : i + 1]]
        ma = sum(window_prices) / len(window_prices)
        result.append({**point, "moving_avg": round(ma, 2)})
    return result


# ══════════════════════════════════════════
# 1. 자재 목록 / 검색
# ══════════════════════════════════════════

class MaterialListView(generics.ListAPIView):
    """
    GET /api/v1/materials/
    ?name=철근 &ks_code=KS+D+3504 &category=structural
    """
    serializer_class = MaterialListSerializer

    def get_queryset(self):
        qs = Material.objects.select_related("spec", "regulation").all()
        name     = self.request.query_params.get("name")
        ks_code  = self.request.query_params.get("ks_code")
        category = self.request.query_params.get("category")

        if name:
            qs = qs.filter(name__icontains=name)
        if ks_code:
            qs = qs.filter(ks_code__icontains=ks_code)
        if category:
            qs = qs.filter(category=category)

        return qs.order_by("id")


# ══════════════════════════════════════════
# 2. 대체 공급사 추천 ← 핵심 엔드포인트
# ══════════════════════════════════════════

@api_view(["POST"])
def alternative_suppliers(request, material_id: int):
    """
    POST /api/v1/materials/{material_id}/alternatives/

    Body:
        site_lat              (float, 필수)
        site_lng              (float, 필수)
        required_yield_strength  (float, 선택 — 없으면 원본 자재 기준값 사용)
        required_tensile_strength (float, 선택)
        is_seismic            (bool,  선택, 기본 False)
        include_international (bool,  선택, 기본 True)
        radius_km             (float, 선택, 기본 50km)
    """

    # ── 원본 자재 조회
    try:
        original = Material.objects.select_related("spec", "regulation").get(pk=material_id)
    except Material.DoesNotExist:
        return Response({"error": "자재를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    if not hasattr(original, "spec"):
        return Response({"error": "해당 자재의 물성 데이터가 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

    # ── 요청 파라미터 파싱
    try:
        site_lat = float(request.data["site_lat"])
        site_lng = float(request.data["site_lng"])
    except (KeyError, ValueError):
        return Response({"error": "site_lat, site_lng 값이 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

    is_seismic           = bool(request.data.get("is_seismic", False))
    include_international = bool(request.data.get("include_international", True))
    radius_km            = float(request.data.get("radius_km", 50))

    orig_spec = original.spec
    min_yield    = float(request.data.get("required_yield_strength",   orig_spec.yield_strength_min))
    min_tensile  = float(request.data.get("required_tensile_strength", orig_spec.tensile_strength_min))
    min_elongation = float(orig_spec.elongation_min)

    # ══════════════════════════════
    # STEP 1: 물성치 기반 동등성 필터
    # ══════════════════════════════
    candidate_specs = MaterialSpec.objects.select_related(
        "material", "material__regulation"
    ).filter(
        yield_strength_min__gte=min_yield,
        tensile_strength_min__gte=min_tensile,
        elongation_min__gte=min_elongation,
        material__category=original.category,
    ).exclude(material=original)

    if is_seismic:
        candidate_specs = candidate_specs.filter(material__is_seismic=True)

    candidate_material_ids = list(candidate_specs.values_list("material_id", flat=True))

    if not candidate_material_ids:
        return Response({
            "original_material": MaterialDetailSerializer(original).data,
            "recommendations": [],
            "message": "동등 물성치를 만족하는 대체 자재가 없습니다.",
        })

    # ══════════════════════════════
    # STEP 2: 공급사 필터 (반경 + 납품 실적 있는 업체만)
    # ══════════════════════════════
    # 좌표가 있는 공급사 중 납품 이력에 후보 자재가 있는 업체를 가져온다.
    histories = (
        SupplyHistory.objects
        .filter(material_id__in=candidate_material_ids)
        .select_related("supplier", "material", "material__spec", "material__regulation")
        .order_by("supplier_id", "material_id", "-contract_date")
    )

    # 공급사 × 자재별로 최신 단가와 납품 횟수를 집계
    supplier_material_map: dict[tuple, dict] = {}
    for h in histories:
        key = (h.supplier_id, h.material_id)
        if key not in supplier_material_map:
            supplier_material_map[key] = {
                "supplier":      h.supplier,
                "material":      h.material,
                "latest_price":  h.unit_price,
                "supply_count":  0,
            }
        supplier_material_map[key]["supply_count"] += 1

    if not supplier_material_map:
        return Response({
            "original_material": MaterialDetailSerializer(original).data,
            "recommendations": [],
            "message": "납품 실적이 있는 공급사가 없습니다.",
        })

    # 반경 필터링 + 거리 계산
    candidates = []
    for (sup_id, mat_id), info in supplier_material_map.items():
        supplier = info["supplier"]
        if not supplier.has_coordinates:
            continue
        dist = haversine(site_lat, site_lng, supplier.latitude, supplier.longitude)
        if dist > radius_km:
            continue
        candidates.append({**info, "distance_km": dist})

    if not candidates:
        return Response({
            "original_material": MaterialDetailSerializer(original).data,
            "recommendations": [],
            "message": f"반경 {radius_km}km 내 납품 실적 공급사가 없습니다.",
        })

    # ══════════════════════════════
    # STEP 3: 가중치 스코어링
    # 가격 40% + 거리 30% + 신뢰도(납품횟수) 30%
    # ══════════════════════════════
    all_prices       = [float(c["latest_price"]) for c in candidates]
    all_counts       = [c["supply_count"]  for c in candidates]
    all_distances    = [c["distance_km"]   for c in candidates]

    min_price     = min(all_prices)
    max_count     = max(all_counts)
    max_distance  = max(all_distances) if max(all_distances) > 0 else 1

    for c in candidates:
        price     = float(c["latest_price"])
        count     = c["supply_count"]
        distance  = c["distance_km"]

        price_score      = (min_price / price)          * 0.4
        distance_score   = (1 - distance / max_distance) * 0.3   # 가까울수록 높은 점수
        reliability_score = (count / max_count)          * 0.3

        c["total_score"] = round(price_score + distance_score + reliability_score, 4)
        c["scores"] = {
            "price_score":        round(price_score, 4),
            "distance_score":     round(distance_score, 4),
            "reliability_score":  round(reliability_score, 4),
            "total":              c["total_score"],
        }

    # 점수 내림차순 정렬 → 상위 3개
    ranked = sorted(candidates, key=lambda x: x["total_score"], reverse=True)[:3]

    # ══════════════════════════════
    # STEP 4: 응답 조립
    # ══════════════════════════════
    recommendations = []
    for i, c in enumerate(ranked, start=1):
        material   = c["material"]
        regulation = getattr(material, "regulation", None)

        # 감리 승인 경고: 원본 자재보다 강도가 상향된 경우
        approval_warning = None
        if regulation and regulation.requires_approval:
            approval_warning = regulation.approval_reason or "감리 승인이 필요합니다. 구조 재계산을 확인하세요."

        recommendations.append({
            "rank":             i,
            "supplier":         c["supplier"],
            "material":         material,
            "scores":           c["scores"],
            "latest_unit_price": c["latest_price"],
            "supply_count":     c["supply_count"],
            "distance_km":      round(c["distance_km"], 2),
            "approval_warning": approval_warning,
        })

    serializer = AlternativeResponseSerializer({
        "original_material": original,
        "recommendations":   recommendations,
    })
    return Response(serializer.data)


# ══════════════════════════════════════════
# 3. 단가 트렌드 (이동평균)
# ══════════════════════════════════════════

@api_view(["GET"])
def price_trend(request, material_id: int):
    """
    GET /api/v1/materials/{material_id}/price-trend/
    ?period=6m  (3m / 6m / 12m, 기본 6m)
    """
    try:
        material = Material.objects.get(pk=material_id)
    except Material.DoesNotExist:
        return Response({"error": "자재를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    period_map = {"3m": 3, "6m": 6, "12m": 12}
    period_str = request.query_params.get("period", "6m")
    months     = period_map.get(period_str, 6)

    since = date.today() - timedelta(days=months * 30)

    histories = (
        SupplyHistory.objects
        .filter(material=material, contract_date__gte=since)
        .values("contract_date__year", "contract_date__month")
        .annotate(avg_price=Avg("unit_price"))
        .order_by("contract_date__year", "contract_date__month")
    )

    if not histories:
        return Response({"error": "해당 기간 단가 데이터가 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    raw = [
        {
            "date":      date(h["contract_date__year"], h["contract_date__month"], 1),
            "avg_price": round(float(h["avg_price"]), 2),
        }
        for h in histories
    ]

    data_with_ma = moving_average(raw, window=3)

    # 인사이트: 현재 단가 vs 기간 내 최저가 비교
    current_price = data_with_ma[-1]["avg_price"]
    min_price_in_period = min(d["avg_price"] for d in data_with_ma)

    if current_price <= min_price_in_period * 1.02:
        insight = f"현재 단가는 최근 {period_str} 내 최저 수준입니다. 선확보를 검토하세요."
    elif current_price >= min_price_in_period * 1.15:
        insight = f"현재 단가는 최근 {period_str} 내 최저가 대비 15% 이상 높습니다."
    else:
        insight = f"현재 단가는 최근 {period_str} 평균 수준입니다."

    serializer = PriceTrendSerializer({
        "material_id": material_id,
        "period":      period_str,
        "data":        data_with_ma,
        "insight":     insight,
    })
    return Response(serializer.data)


# ══════════════════════════════════════════
# 4. 수요 등록
# ══════════════════════════════════════════

class DemandCreateView(generics.CreateAPIView):
    """
    POST /api/v1/demands/
    """
    serializer_class = DemandSerializer
    queryset = Demand.objects.all()
