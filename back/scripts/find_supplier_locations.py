#!/usr/bin/env python3
"""
좌표가 없는 Supplier의 실제 사업장 위치 후보를 Kakao Local Search로 찾는 스크립트.

주의:
- 기존 Supplier.address가 조달청/교육청/공사 등 발주기관 주소일 수 있으므로,
  이 스크립트는 기존 address를 좌표 변환하지 않는다.
- Supplier.name 기반 키워드 검색 결과만 후보로 출력한다.
- --apply 옵션이 있을 때만 DB를 저장한다.
- 자동 저장은 후보가 1개이고 회사명 유사도 HIGH이며 대한민국 좌표인 경우에만 허용한다.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests


BACK_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACK_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402

django.setup()

from django.conf import settings  # noqa: E402
from django.db.models import Count, Q  # noqa: E402

from core.models import Supplier, SupplyHistory  # noqa: E402


KAKAO_LOCAL_SEARCH_URL = "https://dapi.kakao.com/v2/local/search/keyword.json"
KOREA_LATITUDE_RANGE = (33.0, 39.0)
KOREA_LONGITUDE_RANGE = (124.0, 132.0)

AGENCY_ADDRESS_KEYWORDS = [
    "조달청",
    "지방조달청",
    "서울주택도시개발공사",
    "한국공항공사",
    "법무부",
    "교육청",
    "학교",
    "시청",
    "군청",
    "구청",
    "사업소",
    "관리사업소",
    "맑은물사업소",
    "맑은물사업본부",
    "종합건설본부",
    "본부",
    "센터",
    "공사",
    "공단",
    "건강보험심사평가원",
]

COMPANY_REMOVE_PATTERNS = [
    r"\(주\)",
    r"㈜",
    r"주식회사",
    r"\(유\)",
    r"유한회사",
    r"합자회사",
    r"합명회사",
    r"농업회사법인",
    r"회사",
]


@dataclass
class PlaceCandidate:
    query: str
    place_name: str
    road_address_name: str
    address_name: str
    longitude: float | None
    latitude: float | None
    phone: str
    category_name: str
    place_url: str
    confidence: str
    confidence_reason: str


def compact_text(value: str | None) -> str:
    return re.sub(r"\s+", "", value or "")


def is_agency_address(address: str | None) -> bool:
    normalized = compact_text(address)
    if not normalized:
        return False
    return any(keyword in normalized for keyword in AGENCY_ADDRESS_KEYWORDS)


def strip_company_words(value: str | None) -> str:
    text = value or ""
    for pattern in COMPANY_REMOVE_PATTERNS:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", text).strip()


def normalize_company_name(value: str | None) -> str:
    text = strip_company_words(value)
    text = re.sub(r"[^0-9A-Za-z가-힣]", "", text)
    return text.lower()


def is_korea_coordinate(latitude: float | None, longitude: float | None) -> bool:
    if latitude is None or longitude is None:
        return False
    return (
        KOREA_LATITUDE_RANGE[0] <= latitude <= KOREA_LATITUDE_RANGE[1]
        and KOREA_LONGITUDE_RANGE[0] <= longitude <= KOREA_LONGITUDE_RANGE[1]
    )


def parse_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def get_kakao_api_key() -> tuple[str, str]:
    if getattr(settings, "KAKAO_REST_API_KEY", ""):
        return "KAKAO_REST_API_KEY", settings.KAKAO_REST_API_KEY
    if os.getenv("KAKAO_REST_API_KEY"):
        return "KAKAO_REST_API_KEY", os.getenv("KAKAO_REST_API_KEY", "")
    if os.getenv("KAKAO_API_KEY"):
        return "KAKAO_API_KEY", os.getenv("KAKAO_API_KEY", "")
    raise RuntimeError("KAKAO_REST_API_KEY 또는 KAKAO_API_KEY 환경변수가 필요합니다.")


def kakao_keyword_search(query: str, api_key: str, size: int = 5) -> list[dict[str, Any]]:
    response = requests.get(
        KAKAO_LOCAL_SEARCH_URL,
        headers={"Authorization": f"KakaoAK {api_key}"},
        params={"query": query, "size": size},
        timeout=8,
    )
    if response.status_code in (401, 403):
        raise RuntimeError(f"카카오 API 인증 오류 HTTP {response.status_code}")
    if response.status_code != 200:
        raise RuntimeError(f"카카오 API 오류 HTTP {response.status_code}: {response.text[:200]}")
    return response.json().get("documents", [])


def get_representative_material_name(supplier: Supplier) -> str:
    row = (
        SupplyHistory.objects.filter(supplier=supplier)
        .values("material__name")
        .annotate(total=Count("id"))
        .order_by("-total", "material__name")
        .first()
    )
    return (row or {}).get("material__name") or ""


def build_queries(supplier: Supplier) -> list[str]:
    base_name = strip_company_words(supplier.name) or supplier.name
    representative_material = get_representative_material_name(supplier)
    raw_queries = [
        base_name,
        f"{base_name} {representative_material}".strip(),
        f"{base_name} 공장",
        f"{base_name} 본사",
    ]

    queries = []
    for query in raw_queries:
        if query and query not in queries:
            queries.append(query)
    return queries


def judge_confidence(supplier_name: str, place_name: str, candidate_count: int) -> tuple[str, str]:
    supplier_core = normalize_company_name(supplier_name)
    place_core = normalize_company_name(place_name)

    if not supplier_core or not place_core:
        return "LOW", "회사명 비교값 부족"

    if supplier_core == place_core or supplier_core in place_core or place_core in supplier_core:
        if candidate_count == 1:
            return "HIGH", "회사명 핵심어가 일치하고 후보가 1개"
        return "MEDIUM", "회사명 핵심어는 일치하지만 후보가 여러 개"

    for token_length in range(min(len(supplier_core), 6), 2, -1):
        for start in range(0, len(supplier_core) - token_length + 1):
            token = supplier_core[start : start + token_length]
            if token and token in place_core:
                return "MEDIUM", f"회사명 일부 토큰({token}) 일치"

    return "LOW", "회사명 핵심어 불일치"


def to_candidate(document: dict[str, Any], query: str, supplier: Supplier, candidate_count: int) -> PlaceCandidate:
    longitude = parse_float(document.get("x"))
    latitude = parse_float(document.get("y"))
    confidence, reason = judge_confidence(supplier.name, document.get("place_name", ""), candidate_count)

    if not is_korea_coordinate(latitude, longitude):
        confidence = "LOW"
        reason = "좌표 없음 또는 대한민국 범위 밖"

    return PlaceCandidate(
        query=query,
        place_name=document.get("place_name", ""),
        road_address_name=document.get("road_address_name", ""),
        address_name=document.get("address_name", ""),
        longitude=longitude,
        latitude=latitude,
        phone=document.get("phone", ""),
        category_name=document.get("category_name", ""),
        place_url=document.get("place_url", ""),
        confidence=confidence,
        confidence_reason=reason,
    )


def find_candidates(supplier: Supplier, api_key: str) -> tuple[str, list[PlaceCandidate]]:
    for query in build_queries(supplier):
        print(f"  query: {query}")
        documents = kakao_keyword_search(query, api_key)
        if documents:
            candidates = [
                to_candidate(document, query, supplier, len(documents))
                for document in documents
            ]
            return query, candidates
        print("    후보 없음")
        time.sleep(0.15)
    return "", []


def print_candidate(candidate: PlaceCandidate, index: int) -> None:
    print(f"  후보 {index}:")
    print(f"    place_name: {candidate.place_name or '-'}")
    print(f"    road_address_name: {candidate.road_address_name or '-'}")
    print(f"    address_name: {candidate.address_name or '-'}")
    print(f"    x(longitude): {candidate.longitude}")
    print(f"    y(latitude): {candidate.latitude}")
    print(f"    phone: {candidate.phone or '-'}")
    print(f"    category_name: {candidate.category_name or '-'}")
    print(f"    place_url: {candidate.place_url or '-'}")
    print(f"    confidence: {candidate.confidence} ({candidate.confidence_reason})")


def update_supplier(supplier: Supplier, candidate: PlaceCandidate) -> None:
    supplier.address = candidate.road_address_name or candidate.address_name
    supplier.latitude = candidate.latitude
    supplier.longitude = candidate.longitude
    supplier.save(update_fields=["address", "latitude", "longitude", "updated_at"])


def process_supplier(supplier: Supplier, api_key: str, apply: bool) -> str:
    print(f"\n[검색 대상] {supplier.name} / 기존 address={supplier.address or '-'}")

    if is_agency_address(supplier.address):
        print("  기존 address는 기관/발주처 주소로 의심되어 좌표 변환에 사용하지 않습니다.")

    _, candidates = find_candidates(supplier, api_key)
    if not candidates:
        print("  결과: 후보 없음")
        return "no_candidate"

    for index, candidate in enumerate(candidates, start=1):
        print_candidate(candidate, index)

    if len(candidates) != 1:
        print("  결과: 후보가 여러 개입니다. 자동 저장하지 않습니다. 수동 검토 필요")
        return "manual_review"

    candidate = candidates[0]
    if candidate.confidence != "HIGH":
        print("  결과: HIGH 신뢰도 후보가 아니므로 자동 저장하지 않습니다. 수동 검토 필요")
        return "manual_review"

    if not is_korea_coordinate(candidate.latitude, candidate.longitude):
        print("  결과: 대한민국 범위의 유효 좌표가 아니므로 저장하지 않습니다.")
        return "invalid_coordinate"

    if not apply:
        print("  결과: dry-run, 저장 안 함")
        return "dry_run_high"

    update_supplier(supplier, candidate)
    print("  결과: 저장 완료")
    return "updated"


def get_target_suppliers(name: str | None, limit: int | None) -> list[Supplier]:
    queryset = Supplier.objects.filter(Q(latitude__isnull=True) | Q(longitude__isnull=True)).order_by("id")
    if name:
        queryset = queryset.filter(name__icontains=name)
    if limit:
        queryset = queryset[:limit]
    return list(queryset)


def print_supplier_counts(title: str) -> None:
    total = Supplier.objects.count()
    with_coordinates = Supplier.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True).count()
    without_coordinates = Supplier.objects.filter(Q(latitude__isnull=True) | Q(longitude__isnull=True)).count()
    print(f"\n[{title}]")
    print(f"전체 Supplier: {total}")
    print(f"좌표 있음: {with_coordinates}")
    print(f"좌표 없음: {without_coordinates}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="좌표 없는 Supplier의 실제 사업장 위치 후보를 검색합니다.")
    parser.add_argument("--name", help="특정 공급사명만 부분 검색")
    parser.add_argument("--limit", type=int, help="검색 대상 개수 제한")
    parser.add_argument("--dry-run", action="store_true", help="DB 저장 없이 후보만 출력. 기본 동작")
    parser.add_argument("--apply", action="store_true", help="HIGH 신뢰도 단일 후보만 DB에 저장")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    apply = bool(args.apply)

    try:
        key_name, api_key = get_kakao_api_key()
    except RuntimeError as exc:
        print(f"[오류] {exc}")
        return 1

    print(f"[카카오 API 키] {key_name}")
    if apply:
        print("[실행 모드] apply: HIGH 신뢰도 단일 후보만 저장합니다.")
    else:
        print("[실행 모드] dry-run: DB에 저장하지 않습니다. 실제 저장은 --apply 옵션이 필요합니다.")

    print_supplier_counts("실행 전")
    suppliers = get_target_suppliers(args.name, args.limit)
    print(f"\n검색 대상 Supplier: {len(suppliers)}개")

    summary = {
        "updated": 0,
        "dry_run_high": 0,
        "manual_review": 0,
        "no_candidate": 0,
        "invalid_coordinate": 0,
        "error": 0,
    }

    for supplier in suppliers:
        try:
            result = process_supplier(supplier, api_key, apply)
            summary[result] = summary.get(result, 0) + 1
        except requests.RequestException as exc:
            summary["error"] += 1
            print(f"  결과: 카카오 API 요청 오류 - {exc.__class__.__name__}")
        except RuntimeError as exc:
            summary["error"] += 1
            print(f"  결과: 오류 - {exc}")
        time.sleep(0.2)

    print("\n[처리 요약]")
    print(f"저장 완료: {summary['updated']}")
    print(f"dry-run 저장 가능 후보: {summary['dry_run_high']}")
    print(f"수동 검토 필요: {summary['manual_review']}")
    print(f"후보 없음: {summary['no_candidate']}")
    print(f"좌표 오류: {summary['invalid_coordinate']}")
    print(f"API/처리 오류: {summary['error']}")
    print_supplier_counts("실행 후")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
