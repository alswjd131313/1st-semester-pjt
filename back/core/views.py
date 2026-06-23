import math
import re
import requests
import secrets
import string
from concurrent.futures import ThreadPoolExecutor, as_completed
from decimal import Decimal
from datetime import date, timedelta
from collections import defaultdict

from django.db.models import (
    Avg, Case, Count, Exists, F, IntegerField, Max, Min,
    OuterRef, Q, Subquery, When,
)
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated, SAFE_METHODS
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import (
    Material, MaterialSpec, Supplier, SupplyHistory, Demand, SupplierMaterialRegistration,
    CommunityPost, CommunityComment, CommunityContactRequest,
)
from .serializers import (
    MaterialListSerializer,
    MaterialSuggestionSerializer,
    MaterialDetailSerializer,
    AlternativeResponseSerializer,
    PriceTrendSerializer,
    DemandSerializer,
    SupplierMaterialRegistrationSerializer,
    CommunityPostSerializer,
    CommunityCommentSerializer,
    CommunityContactRequestSerializer,
)
from .services.kakao_directions import get_driving_route


JUSO_SEARCH_URL = "https://business.juso.go.kr/addrlink/addrLinkApi.do"
KAKAO_ADDRESS_SEARCH_URL = "https://dapi.kakao.com/v2/local/search/address.json"
KAKAO_KEYWORD_SEARCH_URL = "https://dapi.kakao.com/v2/local/search/keyword.json"
NARAJANGTEO_CONTRACT_SEARCH_URL = "https://apis.data.go.kr/1230000/ao/CntrctInfoService/getCntrctInfoListThngPPSSrch"

SUPPLIER_ADDRESS_FIELDS = ("corpAddr", "cntrctCorpAddr", "spldmdCorpAddr")
AGENCY_ADDRESS_FIELDS = ("dminsttAddr", "cntrctInsttAddr", "dminsttNm", "cntrctInsttNm")


def clean_address_keyword(keyword: str) -> str:
    return re.sub(r"[%=><\[\]]", "", keyword).strip()


@api_view(["GET"])
def search_addresses(request):
    keyword = clean_address_keyword(request.query_params.get("keyword", ""))
    if len(keyword) < 2:
        return Response({"error": "주소 검색어를 두 글자 이상 입력해 주세요."}, status=status.HTTP_400_BAD_REQUEST)
    if not settings.JUSO_API_KEY:
        return Response({"error": "도로명주소 검색 API 키가 설정되지 않았습니다."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    try:
        response = requests.get(
            JUSO_SEARCH_URL,
            params={
                "confmKey": settings.JUSO_API_KEY,
                "currentPage": 1,
                "countPerPage": 8,
                "keyword": keyword,
                "resultType": "json",
                "firstSort": "road",
            },
            timeout=8,
        )
        response.raise_for_status()
        results = response.json().get("results", {})
        common = results.get("common", {})
        if common.get("errorCode") != "0":
            return Response({"error": common.get("errorMessage", "주소 검색에 실패했습니다.")}, status=status.HTTP_400_BAD_REQUEST)

        addresses = [
            {
                "roadAddress": item.get("roadAddrPart1") or item.get("roadAddr"),
                "fullRoadAddress": item.get("roadAddr"),
                "jibunAddress": item.get("jibunAddr"),
                "zipNo": item.get("zipNo"),
                "buildingName": item.get("bdNm"),
                "buildingManagementNo": item.get("bdMgtSn"),
            }
            for item in results.get("juso", [])
        ]
        return Response({"addresses": addresses, "totalCount": int(common.get("totalCount", 0))})
    except (requests.RequestException, ValueError):
        return Response({"error": "도로명주소 서비스에 연결하지 못했습니다."}, status=status.HTTP_502_BAD_GATEWAY)


@api_view(["GET"])
def geocode_address(request):
    address = request.query_params.get("address", "").strip()
    if not address:
        return Response({"error": "좌표로 변환할 주소가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)
    if not settings.KAKAO_REST_API_KEY:
        return Response({"error": "카카오 REST API 키가 설정되지 않았습니다."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    try:
        response = requests.get(
            KAKAO_ADDRESS_SEARCH_URL,
            headers={"Authorization": f"KakaoAK {settings.KAKAO_REST_API_KEY}"},
            params={"query": address, "analyze_type": "exact"},
            timeout=8,
        )
        data = response.json()
        if response.status_code == 403:
            return Response(
                {"error": "카카오 개발자 콘솔에서 지도/로컬 API 서비스를 활성화해 주세요."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        response.raise_for_status()
        documents = data.get("documents", [])
        if not documents:
            return Response({"error": "선택한 주소의 좌표를 찾지 못했습니다."}, status=status.HTTP_404_NOT_FOUND)

        result = documents[0]
        return Response({
            "address": result.get("address_name", address),
            "latitude": round(float(result["y"]), 6),
            "longitude": round(float(result["x"]), 6),
        })
    except (requests.RequestException, ValueError, KeyError):
        return Response({"error": "카카오 좌표 변환 서비스에 연결하지 못했습니다."}, status=status.HTTP_502_BAD_GATEWAY)


@api_view(["GET"])
def narajangteo_contracts(request):
    keyword = request.query_params.get("keyword", "").strip()
    year = request.query_params.get("year", str(date.today().year))
    page = request.query_params.get("page", "1")
    try:
        rows = min(max(int(request.query_params.get("rows", 10)), 1), 30)
    except (TypeError, ValueError):
        rows = 10

    if len(keyword) < 2:
        return Response({"error": "계약 검색어를 두 글자 이상 입력해 주세요."}, status=status.HTTP_400_BAD_REQUEST)
    if not settings.NARAJANGTEO_API_KEY:
        return Response({"error": "나라장터 계약정보서비스 API 키가 설정되지 않았습니다."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    try:
        response = requests.get(
            NARAJANGTEO_CONTRACT_SEARCH_URL,
            params={
                "ServiceKey": settings.NARAJANGTEO_API_KEY,
                "numOfRows": rows,
                "pageNo": page,
                "inqryDiv": "1",
                "inqryBgnDate": f"{year}0101",
                "inqryEndDate": f"{year}1231",
                "prdctClsfcNoNm": keyword,
                "type": "json",
            },
            timeout=12,
        )
        response.raise_for_status()
        try:
            payload = response.json()
        except ValueError:
            return Response(
                {
                    "error": "나라장터 계약정보서비스 응답을 JSON으로 해석하지 못했습니다.",
                    "statusCode": response.status_code,
                    "contentType": response.headers.get("content-type", ""),
                    "preview": response.text[:300],
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        body = payload.get("response", {}).get("body", {})
        raw_items = body.get("items", [])
        if isinstance(raw_items, dict):
            raw_items = raw_items.get("item", [])
        if isinstance(raw_items, dict):
            raw_items = [raw_items]

        contracts = [normalize_narajangteo_contract(item) for item in raw_items if isinstance(item, dict)]
        return Response({
            "keyword": keyword,
            "year": year,
            "totalCount": int(body.get("totalCount", 0) or 0),
            "contracts": contracts,
        })
    except requests.Timeout:
        return Response(
            {"error": "나라장터 계약정보서비스 응답이 지연되고 있습니다. 잠시 후 다시 시도해 주세요."},
            status=status.HTTP_504_GATEWAY_TIMEOUT,
        )
    except requests.RequestException as exc:
        return Response(
            {"error": "나라장터 계약정보서비스에 연결하지 못했습니다.", "detail": exc.__class__.__name__},
            status=status.HTTP_502_BAD_GATEWAY,
        )
    except (ValueError, TypeError) as exc:
        return Response(
            {"error": "나라장터 계약정보서비스 응답을 처리하지 못했습니다.", "detail": exc.__class__.__name__},
            status=status.HTTP_502_BAD_GATEWAY,
        )


@api_view(["GET"])
def cached_narajangteo_contracts(request):
    keyword = request.query_params.get("keyword", "").strip()
    rows = request.query_params.get("rows", 20)
    include_seed = request.query_params.get("include_seed", "").lower() in {"1", "true", "yes"}

    try:
        rows = min(max(int(rows), 1), 50)
    except (TypeError, ValueError):
        rows = 20

    source_filter = Q(supplier__source="narajangteo")
    if include_seed:
        source_filter |= Q(raw_data__source="PaceFlow MVP seed")

    histories = (
        SupplyHistory.objects
        .select_related("supplier", "material")
        .filter(source_filter)
        .annotate(
            delivery_count=Count(
                "supplier__supply_histories",
                filter=Q(supplier__supply_histories__material_id=F("material_id")),
            )
        )
        .order_by("-contract_date")
    )

    if keyword:
        histories = histories.filter(
            Q(material__name__icontains=keyword)
            | Q(material__ks_code__icontains=keyword)
            | Q(material__ks_grade__icontains=keyword)
            | Q(material__diameter__icontains=keyword)
            | Q(supplier__name__icontains=keyword)
        )

    contracts = []
    seen_contracts = set()
    for history in histories[: rows * 8]:
        raw = history.raw_data or {}
        dedupe_key = (
            history.supplier_id,
            history.contract_date,
            str(history.unit_price),
            raw.get("cntrctNm") or raw.get("contractName") or str(history.material),
        )
        if dedupe_key in seen_contracts:
            continue
        seen_contracts.add(dedupe_key)
        contracts.append(serialize_cached_contract(history))
        if len(contracts) >= rows:
            break

    return Response({
        "keyword": keyword,
        "source": "cached_supply_history",
        "totalCount": histories.count(),
        "contracts": contracts,
    })


def serialize_cached_contract(history: SupplyHistory) -> dict:
    raw = history.raw_data or {}
    location = resolve_contract_location(raw, history.supplier)
    return {
        "supplierName": history.supplier.name,
        "productName": str(history.material),
        "contractName": raw.get("cntrctNm") or raw.get("contractName") or str(history.material),
        "contractDate": history.contract_date.isoformat(),
        "contractAmount": str(history.unit_price),
        "demandAgency": raw.get("dminsttNm") or raw.get("cntrctInsttNm") or "",
        "supplierAddress": first_present(raw, SUPPLIER_ADDRESS_FIELDS) or history.supplier.address,
        "locationLabel": location["label"],
        "locationBasis": location["basis"],
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "supplierDistanceAvailable": location["basis"] == "supplier_address",
        "matchBasis": raw.get("paceflowMatchBasis") or "기존 수집 데이터",
        "deliveryCount": getattr(history, "delivery_count", 1),
        "source": raw.get("source") or history.supplier.source,
    }


def normalize_narajangteo_contract(item: dict) -> dict:
    supplier_name = parse_narajangteo_supplier_name(item.get("corpList", ""))
    amount = item.get("thtmCntrctAmt") or item.get("cntrctAmt") or ""
    location = resolve_contract_location(item)
    return {
        "supplierName": supplier_name or "계약업체 확인 필요",
        "productName": item.get("prdctClsfcNoNm") or item.get("prdctClsfcNoNmNm") or item.get("cntrctNm") or "품명 확인 필요",
        "contractName": item.get("cntrctNm") or "",
        "contractDate": item.get("cntrctCnclsDate") or item.get("cntrctDate") or "",
        "contractAmount": amount,
        "demandAgency": item.get("dminsttNm") or item.get("cntrctInsttNm") or "",
        "supplierAddress": first_present(item, SUPPLIER_ADDRESS_FIELDS),
        "locationLabel": location["label"],
        "locationBasis": location["basis"],
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "supplierDistanceAvailable": location["basis"] == "supplier_address",
        "raw": item,
    }


def first_present(source: dict, fields: tuple[str, ...]) -> str:
    for field in fields:
        value = str(source.get(field, "") or "").strip()
        if value:
            return value
    return ""


def resolve_contract_location(raw: dict, supplier: Supplier | None = None) -> dict:
    if supplier and supplier.has_coordinates:
        return {
            "basis": "supplier_address",
            "label": supplier.address or supplier.name,
            "latitude": float(supplier.latitude),
            "longitude": float(supplier.longitude),
        }

    supplier_address = first_present(raw, SUPPLIER_ADDRESS_FIELDS) or (supplier.address if supplier else "")
    if supplier_address:
        coords = geocode_with_kakao_address(supplier_address)
        if coords:
            return {
                "basis": "supplier_address",
                "label": supplier_address,
                **coords,
            }

    agency_location = first_present(raw, AGENCY_ADDRESS_FIELDS)
    if agency_location:
        coords = geocode_with_kakao_address(agency_location) or search_kakao_place(agency_location)
        if coords:
            return {
                "basis": "contract_agency_estimated",
                "label": agency_location,
                **coords,
            }

    return {
        "basis": "unknown",
        "label": supplier.name if supplier else first_present(raw, ("cntrctInsttNm", "dminsttNm")),
        "latitude": None,
        "longitude": None,
    }


def geocode_with_kakao_address(address: str) -> dict | None:
    if not address or not settings.KAKAO_REST_API_KEY:
        return None
    try:
        response = requests.get(
            KAKAO_ADDRESS_SEARCH_URL,
            headers={"Authorization": f"KakaoAK {settings.KAKAO_REST_API_KEY}"},
            params={"query": address},
            timeout=4,
        )
        response.raise_for_status()
        documents = response.json().get("documents", [])
        if not documents:
            return None
        result = documents[0]
        return {
            "latitude": round(float(result["y"]), 6),
            "longitude": round(float(result["x"]), 6),
        }
    except (requests.RequestException, ValueError, KeyError):
        return None


def search_kakao_place(keyword: str) -> dict | None:
    if not keyword or not settings.KAKAO_REST_API_KEY:
        return None
    try:
        response = requests.get(
            KAKAO_KEYWORD_SEARCH_URL,
            headers={"Authorization": f"KakaoAK {settings.KAKAO_REST_API_KEY}"},
            params={"query": keyword, "size": 1},
            timeout=4,
        )
        response.raise_for_status()
        documents = response.json().get("documents", [])
        if not documents:
            return None
        result = documents[0]
        return {
            "latitude": round(float(result["y"]), 6),
            "longitude": round(float(result["x"]), 6),
        }
    except (requests.RequestException, ValueError, KeyError):
        return None


def parse_narajangteo_supplier_name(corp_list: str) -> str:
    if not corp_list:
        return ""
    first = corp_list.strip("[]").split("],[")[0]
    parts = first.split("^")
    return parts[3].strip() if len(parts) > 3 else ""


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


MATERIAL_SUGGESTION_ALIASES = {
    "철근": {"groups": ["rebar"]},
    "H형강": {"subtypes": ["h_beam"]},
    "H빔": {"subtypes": ["h_beam"]},
    "형강": {"groups": ["shape_steel"]},
    "시멘트": {"groups": ["cement"]},
    "단열재": {"groups": ["insulation"]},
    "전선관": {"groups": ["electrical_conduit"]},
    "전기 배관재": {"groups": ["electrical_conduit"]},
}


@api_view(["GET"])
def material_suggestions(request):
    query = request.query_params.get("q", "").strip()
    if not query:
        return Response([])

    normalized_query = query.casefold()
    group_codes = {
        code for code, label in Material.MATERIAL_GROUP_CHOICES
        if normalized_query in code.casefold() or normalized_query in label.casefold()
    }
    subtype_codes = {
        code for code, label in Material.MATERIAL_SUBTYPE_CHOICES
        if normalized_query in code.casefold() or normalized_query in label.casefold()
    }
    for alias, mapping in MATERIAL_SUGGESTION_ALIASES.items():
        normalized_alias = alias.casefold()
        if normalized_query in normalized_alias or normalized_alias in normalized_query:
            group_codes.update(mapping.get("groups", []))
            subtype_codes.update(mapping.get("subtypes", []))

    filters = (
        Q(name__icontains=query)
        | Q(ks_code__icontains=query)
        | Q(ks_grade__icontains=query)
        | Q(diameter__icontains=query)
        | Q(supply_histories__supplier__name__icontains=query)
    )
    if group_codes:
        filters |= Q(material_group__in=group_codes)
    if subtype_codes:
        filters |= Q(material_subtype__in=subtype_codes)

    recent_history = SupplyHistory.objects.filter(
        material_id=OuterRef("pk")
    ).order_by("-contract_date", "-id")
    queryset = (
        Material.objects.filter(filters)
        .annotate(
            supplier_name=Subquery(recent_history.values("supplier__name")[:1]),
            available=Exists(recent_history),
            match_priority=Case(
                When(name__istartswith=query, then=0),
                When(ks_grade__istartswith=query, then=1),
                When(diameter__istartswith=query, then=2),
                default=3,
                output_field=IntegerField(),
            ),
        )
        .distinct()
        .order_by("match_priority", "name", "ks_grade", "diameter")[:8]
    )
    return Response(MaterialSuggestionSerializer(queryset, many=True).data)


# ══════════════════════════════════════════
# 2. 대체 공급사 추천 ← 핵심 엔드포인트
# ══════════════════════════════════════════


@api_view(["POST"])
def driving_route(request):
    """선택한 현장·공급사 좌표 1건의 차량 경로를 조회한다."""
    result = get_driving_route(
        request.data.get("origin_lat"),
        request.data.get("origin_lng"),
        request.data.get("destination_lat"),
        request.data.get("destination_lng"),
        include_path=True,
    )
    return Response({
        "route_distance_m": result.get("distance_m"),
        "route_duration_sec": result.get("duration_sec"),
        "route_status": result.get("status", "failed"),
        "route_note": result.get("note", "거리 정보 확인 필요"),
        "route_path": result.get("route_path", []),
    })


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

    # ══════════════════════════════════════════════════════
    # STEP 1: 물성치 기반 동등성 필터 (Hard Filter)
    # ① 항복강도·인장강도·연신율·탄소당량 수치 비교
    # ② KS↔ASTM↔JIS 동등성 — include_international=False 시 승인 필요 자재 제외
    # ③ 시공 용도 호환성 — 구조재/비구조재·내진·용접 가능 여부 일치
    # ══════════════════════════════════════════════════════
    candidate_specs = MaterialSpec.objects.select_related(
        "material", "material__regulation"
    ).filter(
        yield_strength_min__gte=min_yield,
        tensile_strength_min__gte=min_tensile,
        elongation_min__gte=min_elongation,
        material__category=original.category,
        material__name=original.name,
    ).exclude(material=original)

    # ① 탄소당량 — 원본 이하만 허용 (높을수록 용접성·가공성 저하)
    if orig_spec.carbon_equivalent_max:
        candidate_specs = candidate_specs.filter(
            carbon_equivalent_max__lte=orig_spec.carbon_equivalent_max
        )

    # ③ 내진 구조 요구 시 내진 적용 가능 자재만
    if is_seismic:
        candidate_specs = candidate_specs.filter(material__is_seismic=True)

    # ③ 원본이 용접 시공 가능인 경우 동일 조건 유지
    if original.is_weldable:
        candidate_specs = candidate_specs.filter(material__is_weldable=True)

    # ② 국제 규격 비포함 시 감리 승인 불필요한 KS 직접 대체재만
    if not include_international:
        candidate_specs = candidate_specs.exclude(
            material__regulation__requires_approval=True
        )

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
                "data_source":   (h.raw_data or {}).get("source") or h.supplier.source,
            }
        supplier_material_map[key]["supply_count"] += 1

    if not supplier_material_map:
        return Response({
            "original_material": MaterialDetailSerializer(original).data,
            "recommendations": [],
            "message": "납품 실적이 있는 공급사가 없습니다.",
        })

    # 직선거리는 API 호출 후보를 제한하는 용도로만 사용한다.
    candidates = []
    for info in supplier_material_map.values():
        supplier = info["supplier"]
        straight_distance_km = None
        if supplier.has_coordinates:
            straight_distance_km = haversine(
                site_lat,
                site_lng,
                supplier.latitude,
                supplier.longitude,
            )
            if straight_distance_km > radius_km:
                continue

        candidates.append({
            **info,
            "straight_distance_km": straight_distance_km,
            "route": {
                "distance_m": None,
                "duration_sec": None,
                "status": "missing_coordinates",
                "note": "거리 정보 확인 필요",
            },
        })

    if not candidates:
        return Response({
            "original_material": MaterialDetailSerializer(original).data,
            "recommendations": [],
            "message": f"반경 {radius_km}km 내 납품 실적 공급사가 없습니다.",
        })

    # 외부 호출 수를 제한하되 가까운 공급사와 납품 이력이 많은 공급사를 우선한다.
    candidates = sorted(
        candidates,
        key=lambda item: (
            item["straight_distance_km"] is None,
            item["straight_distance_km"] if item["straight_distance_km"] is not None else float("inf"),
            -item["supply_count"],
            float(item["latest_price"]),
        ),
    )[:20]

    routable_candidates = [
        candidate
        for candidate in candidates
        if candidate["supplier"].has_coordinates
    ]
    if routable_candidates:
        with ThreadPoolExecutor(max_workers=min(5, len(routable_candidates))) as executor:
            future_map = {
                executor.submit(
                    get_driving_route,
                    candidate["supplier"].latitude,
                    candidate["supplier"].longitude,
                    site_lat,
                    site_lng,
                ): candidate
                for candidate in routable_candidates
            }
            for future in as_completed(future_map):
                candidate = future_map[future]
                try:
                    candidate["route"] = future.result()
                except Exception:
                    candidate["route"] = {
                        "distance_m": None,
                        "duration_sec": None,
                        "status": "api_error",
                        "note": "거리 정보 확인 필요",
                    }

    # 실제 차량 경로가 확인된 후보만 차량 거리로 반경을 재확인한다.
    candidates = [
        candidate
        for candidate in candidates
        if candidate["route"]["status"] != "success"
        or candidate["route"]["distance_m"] / 1000 <= radius_km
    ]

    if not candidates:
        return Response({
            "original_material": MaterialDetailSerializer(original).data,
            "recommendations": [],
            "message": f"차량 경로 기준 반경 {radius_km}km 내 공급사가 없습니다.",
        })

    # ══════════════════════════════
    # STEP 3: 가중치 스코어링
    # KS 적합도 45% + 신뢰도 30% + 차량 경로 15% + 가격 10%
    # 경로 미확인 시 15%를 제외한 나머지 점수를 재정규화한다.
    # ══════════════════════════════
    all_prices       = [float(c["latest_price"]) for c in candidates]
    all_counts       = [c["supply_count"]  for c in candidates]
    successful_routes = [
        c["route"]
        for c in candidates
        if c["route"]["status"] == "success"
    ]

    min_price     = min(all_prices)
    max_count     = max(all_counts)
    min_route_distance = min(
        (route["distance_m"] for route in successful_routes),
        default=None,
    )
    min_route_duration = min(
        (route["duration_sec"] for route in successful_routes),
        default=None,
    )

    for c in candidates:
        price     = float(c["latest_price"])
        count     = c["supply_count"]
        route = c["route"]

        material_fit_score = 100.0
        price_score = (min_price / price) * 100
        reliability_score = (count / max_count) * 100
        route_score = None
        if route["status"] == "success":
            distance_component = (min_route_distance / max(route["distance_m"], 1)) * 100
            duration_component = (min_route_duration / max(route["duration_sec"], 1)) * 100
            route_score = (distance_component + duration_component) / 2

        weighted_score = (
            material_fit_score * 0.45
            + reliability_score * 0.30
            + price_score * 0.10
        )
        known_weight = 0.85
        if route_score is not None:
            weighted_score += route_score * 0.15
            known_weight += 0.15

        c["total_score"] = round(weighted_score / known_weight, 2)
        c["scores"] = {
            "material_fit_score": round(material_fit_score),
            "price_score": round(price_score),
            "distance_score": round(route_score) if route_score is not None else None,
            "route_score": round(route_score) if route_score is not None else None,
            "reliability_score": round(reliability_score),
            "total": c["total_score"],
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

        # ④ 감리 승인 경고 — 승인 필요 자재는 국제 규격 코드(ASTM/JIS)와 함께 상세 안내
        approval_warning = None
        if regulation and regulation.requires_approval:
            intl_codes = []
            if regulation.astm_code and regulation.astm_code != "—":
                intl_codes.append(f"ASTM {regulation.astm_code}")
            if regulation.jis_code and regulation.jis_code != "—":
                intl_codes.append(f"JIS {regulation.jis_code}")
            intl_str = f" (국제 동등 규격: {', '.join(intl_codes)})" if intl_codes else ""
            base_reason = regulation.approval_reason or "감리 승인이 필요합니다. 구조 재계산을 확인하세요."
            approval_warning = f"{base_reason}{intl_str}"

        recommendations.append({
            "rank":             i,
            "supplier":         c["supplier"],
            "material":         material,
            "scores":           c["scores"],
            "latest_unit_price": c["latest_price"],
            "supply_count":     c["supply_count"],
            "distance_km": (
                round(c["route"]["distance_m"] / 1000, 2)
                if c["route"]["status"] == "success"
                else (
                    round(c["straight_distance_km"], 2)
                    if c["straight_distance_km"] is not None
                    else None
                )
            ),
            "route_distance_m": c["route"].get("distance_m"),
            "route_duration_sec": c["route"].get("duration_sec"),
            "route_status": c["route"].get("status", "api_error"),
            "route_note": c["route"].get("note", "거리 정보 확인 필요"),
            "approval_warning": approval_warning,
            "data_source":      c.get("data_source", ""),
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
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if getattr(request.user, "profile", None) and request.user.profile.role != "requester":
            return Response({"error": "자재 요청자 계정만 요청을 등록할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class SupplierMaterialRegistrationListCreateView(generics.ListCreateAPIView):
    """
    GET/POST /api/v1/supplier-materials/
    로그인한 공급사 계정의 직접 등록 자재만 조회/생성한다.
    """
    serializer_class = SupplierMaterialRegistrationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.supplier_material_registrations.all()

    def create(self, request, *args, **kwargs):
        if getattr(request.user, "profile", None) and request.user.profile.role != "supplier":
            return Response({"error": "공급사 계정만 자재를 등록할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class SupplierMaterialRegistrationDetailView(generics.RetrieveDestroyAPIView):
    """로그인한 공급사가 직접 등록한 자재 한 건을 조회하거나 삭제한다."""
    serializer_class = SupplierMaterialRegistrationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.supplier_material_registrations.all()


class PublicSupplierMaterialRegistrationListView(generics.ListAPIView):
    """
    GET /api/v1/supplier-materials/public/
    요청자 추천 결과에 사용할 공급사 직접 등록 자재 전체 공개 목록.
    수정/관리는 등록 공급사 본인만 가능하지만, 문의 후보로는 전체 공개한다.
    """
    serializer_class = SupplierMaterialRegistrationSerializer
    queryset = SupplierMaterialRegistration.objects.select_related("owner").all()


# ══════════════════════════════════════════
# 6. 커뮤니티 MVP
# ══════════════════════════════════════════

class IsCommunityAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj.author == request.user


@api_view(["GET"])
@permission_classes([AllowAny])
def community_public_profile(request, user_id):
    author = generics.get_object_or_404(
        get_user_model().objects.select_related("profile").filter(
            community_posts__display_mode="profile",
        ).distinct(),
        pk=user_id,
    )
    profile = getattr(author, "profile", None)
    role_labels = {"requester": "현장 자재 담당자", "supplier": "공급사 담당자"}
    name = author.first_name or author.username or "PaceFlow 사용자"
    return Response({
        "id": author.id,
        "display_name": name,
        "affiliation": getattr(profile, "company_name", ""),
        "role": role_labels.get(getattr(profile, "role", ""), "PaceFlow 사용자"),
        "project_name": "",
        "avatar_text": (name[:2] or "PF").upper(),
        "community_post_count": author.community_posts.filter(display_mode="profile").count(),
        "received_contact_request_count": author.received_community_contact_requests.filter(
            post__display_mode="profile",
        ).count(),
    })


class CommunityPostListCreateView(generics.ListCreateAPIView):
    serializer_class = CommunityPostSerializer

    def get_queryset(self):
        queryset = CommunityPost.objects.select_related("author", "author__profile").annotate(
            comment_count=Count("comments")
        )
        post_type = self.request.query_params.get("type", "").strip()
        return queryset.filter(post_type=post_type) if post_type else queryset

    def get_permissions(self):
        return [IsAuthenticated()] if self.request.method == "POST" else [AllowAny()]

    def perform_create(self, serializer):
        display_mode = serializer.validated_data.get("display_mode", "profile")
        alias = ""
        if display_mode == "anonymous":
            alphabet = string.ascii_uppercase + string.digits
            alias = "익명" + "".join(secrets.choice(alphabet) for _ in range(5))
        serializer.save(author=self.request.user, anonymous_alias=alias)


class CommunityPostDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommunityPostSerializer
    permission_classes = [IsCommunityAuthorOrReadOnly]
    queryset = CommunityPost.objects.select_related("author", "author__profile").prefetch_related(
        "comments__author", "comments__author__profile"
    ).annotate(comment_count=Count("comments"))

    def perform_update(self, serializer):
        post = self.get_object()
        display_mode = serializer.validated_data.get("display_mode", post.display_mode)
        alias = post.anonymous_alias
        if display_mode == "anonymous" and not alias:
            alphabet = string.ascii_uppercase + string.digits
            alias = "익명" + "".join(secrets.choice(alphabet) for _ in range(5))
        elif display_mode == "profile":
            alias = ""
        serializer.save(author=post.author, anonymous_alias=alias)


class CommunityCommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommunityCommentSerializer

    def get_queryset(self):
        return CommunityComment.objects.filter(post_id=self.kwargs["post_id"]).select_related(
            "author", "author__profile"
        )

    def get_permissions(self):
        return [IsAuthenticated()] if self.request.method == "POST" else [AllowAny()]

    def perform_create(self, serializer):
        post = generics.get_object_or_404(CommunityPost, pk=self.kwargs["post_id"])
        display_mode = serializer.validated_data.get("display_mode", "profile")
        alias = ""
        if display_mode == "anonymous":
            alias = CommunityComment.objects.filter(
                post=post,
                author=self.request.user,
                display_mode="anonymous",
            ).exclude(anonymous_alias="").values_list("anonymous_alias", flat=True).first() or ""
            if not alias:
                alphabet = string.ascii_uppercase + string.digits
                alias = "익명" + "".join(secrets.choice(alphabet) for _ in range(5))
        serializer.save(post=post, author=self.request.user, anonymous_alias=alias)


class CommunityContactRequestListCreateView(generics.ListCreateAPIView):
    serializer_class = CommunityContactRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CommunityContactRequest.objects.filter(
            Q(requester=self.request.user) | Q(recipient=self.request.user)
        ).select_related(
            "post", "post__author", "post__author__profile", "requester", "requester__profile"
        )

    def perform_create(self, serializer):
        post = serializer.validated_data["post"]
        if post.author == self.request.user:
            raise ValidationError({"post": "본인 게시글에는 질문 요청을 보낼 수 없습니다."})
        serializer.save(requester=self.request.user, recipient=post.author, status="pending")


class CommunityContactRequestDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = CommunityContactRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CommunityContactRequest.objects.filter(
            Q(requester=self.request.user) | Q(recipient=self.request.user)
        ).select_related(
            "post", "post__author", "post__author__profile", "requester", "requester__profile"
        )

    def perform_update(self, serializer):
        contact_request = self.get_object()
        if contact_request.recipient != self.request.user:
            raise ValidationError({"status": "작성자만 요청 상태를 변경할 수 있습니다."})
        next_status = serializer.validated_data.get("status", contact_request.status)
        if next_status not in {"pending", "confirmed", "rejected"}:
            raise ValidationError({"status": "올바르지 않은 상태입니다."})
        serializer.save()

    def update(self, request, *args, **kwargs):
        if set(request.data.keys()) - {"status"}:
            return Response(
                {"error": "커뮤니티 대화 요청에서는 상태만 변경할 수 있습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().update(request, *args, **kwargs)
