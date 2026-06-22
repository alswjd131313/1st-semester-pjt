# -*- coding: utf-8 -*-
"""Collect structural steel and electrical conduit candidates from the PPS API."""

import argparse
import hashlib
import math
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from urllib.parse import unquote

import django
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from core.models import Material, Supplier, SupplyHistory


BASE_URL = "http://apis.data.go.kr/1230000/at/ShoppingMallPrdctInfoService"
API_PAGE_SIZE = 10
OPERATIONS = {
    "mas": "getMASCntrctPrdctInfoList",
    "third_party": "getThptyUcntrctPrdctInfoList",
    "registered": "getShoppingMallPrdctInfoList",
}
KAKAO_GEOCODE_URL = "https://dapi.kakao.com/v2/local/search/address.json"
API_KEY = os.getenv("SHOPPING_MALL_API_KEY", "")
KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY", "")

SUPPORTED_MATERIALS = {
    "형강·강재": {
        "db_name": "H빔",
        "subtypes": {
            "H형강": ("H형강", "H빔", "에이치빔"),
            "ㄱ형강": ("ㄱ형강", "앵글", "ANGLE"),
            "ㄷ형강": ("ㄷ형강", "채널", "CHANNEL"),
            "각형강관": ("각형강관", "각관"),
            "강판": ("강판", "STEEL PLATE"),
        },
        "mapped_subtypes": {"H형강"},
        "subtype_codes": {"H형강": "h_beam"},
        "representative": ("KS D 3503", "SS275", "H-300x300"),
    },
    "전기 배관재": {
        "db_name": "전선관",
        "subtypes": {
            "경질 전선관": ("경질전선관", "합성수지제전선관", "PVC전선관"),
            "가요 전선관": ("가요전선관", "플렉시블전선관"),
            "CD관": ("CD관",),
            "PF관": ("PF관",),
        },
        "mapped_subtypes": {"경질 전선관", "가요 전선관", "CD관", "PF관"},
        "subtype_codes": {
            "경질 전선관": "rigid_conduit",
            "가요 전선관": "flexible_conduit",
            "CD관": "cd_conduit",
            "PF관": "pf_conduit",
        },
        "representative": ("KS C IEC 61386-1", "경질 합성수지관", "16C"),
    },
}

MATERIAL_ALIASES = {"H빔": "형강·강재", "전선관": "전기 배관재"}

NON_ELECTRICAL_PIPE_KEYWORDS = (
    "수도관", "상수관", "하수관", "가스관", "급수관", "배수관", "오수관", "소방배관",
)

TEXT_FIELDS = (
    "prdctClsfcNoNm",
    "dtilPrdctClsfcNoNm",
    "prdctSpecNm",
    "prdctDtlInfo",
    "prodctChrInfoIntrcn",
    "prdctMakrNm",
    "cntrctSpcmntMtr",
)


class ApiRateLimitError(RuntimeError):
    pass


def normalize_text(value) -> str:
    return re.sub(r"[^0-9A-Z가-힣]", "", str(value or "").upper())


def item_text(item: dict) -> str:
    return " ".join(str(item.get(field, "")) for field in TEXT_FIELDS if item.get(field))


def fetch_page(operation: str, page: int) -> dict:
    params = {
        "serviceKey": unquote(API_KEY),
        "pageNo": page,
        "numOfRows": API_PAGE_SIZE,
        "inqryDiv": "1",
        "type": "json",
    }
    try:
        response = requests.get(f"{BASE_URL}/{operation}", params=params, timeout=(10, 70))
        if response.status_code == 429:
            raise ApiRateLimitError("종합쇼핑몰 API 호출 한도에 도달했습니다.")
        response.raise_for_status()
        data = response.json()
        header = data.get("response", {}).get("header", {})
        if str(header.get("resultCode", "")) != "00":
            raise RuntimeError(header.get("resultMsg") or "API 응답 오류")
        return data
    except ApiRateLimitError:
        raise
    except (requests.RequestException, ValueError, RuntimeError) as exc:
        status_code = getattr(getattr(exc, "response", None), "status_code", None)
        detail = f"HTTP {status_code}" if status_code else exc.__class__.__name__
        raise RuntimeError(f"종합쇼핑몰 API 호출 실패: {detail}") from exc


def parse_page(data: dict) -> tuple[list[dict], int]:
    body = data.get("response", {}).get("body", {})
    items = body.get("items") or []
    if isinstance(items, dict):
        items = items.get("item") or []
    if not isinstance(items, list):
        items = [items]
    return [item for item in items if isinstance(item, dict)], int(body.get("totalCount") or 0)


def detect_material(item: dict, requested: set[str]) -> tuple[str | None, str, str, str]:
    normalized = normalize_text(item_text(item))
    for group_name in requested:
        config = SUPPORTED_MATERIALS[group_name]
        if group_name == "전기 배관재" and any(
            normalize_text(keyword) in normalized for keyword in NON_ELECTRICAL_PIPE_KEYWORDS
        ):
            continue

        for subtype, keywords in config["subtypes"].items():
            keyword = next(
                (keyword for keyword in keywords if normalize_text(keyword) in normalized),
                None,
            )
            if keyword and subtype in config["mapped_subtypes"]:
                basis = f"종합쇼핑몰 {group_name}/{subtype} 키워드: {keyword}"
                return config["db_name"], group_name, subtype, basis
    return None, "", "", ""


def material_match_score(material: Material, item: dict) -> int:
    text = normalize_text(item_text(item))
    grade = normalize_text(material.ks_grade)
    diameter = normalize_text(material.diameter)
    score = 0

    if grade and grade in text:
        score += 60
    if diameter and diameter in text:
        score += 80

    if material.name == "H빔":
        size = normalize_text(material.diameter.replace("H-", ""))
        if size and size in text:
            score += 80

    if material.name == "전선관":
        if "가요" in text and "가요" in material.ks_grade:
            score += 70
        if any(token in text for token in ("경질", "합성수지", "PVC")) and "경질" in material.ks_grade:
            score += 70

    return score


def choose_materials(
    item: dict,
    material_name: str,
    group_name: str,
    subtype: str,
) -> tuple[list[Material], str]:
    subtype_code = SUPPORTED_MATERIALS[group_name]["subtype_codes"][subtype]
    materials = list(
        Material.objects.filter(
            name=material_name,
            material_subtype=subtype_code,
        )
    )
    scored = sorted(
        ((material_match_score(material, item), material) for material in materials),
        key=lambda pair: pair[0],
        reverse=True,
    )
    exact = [material for score, material in scored if score >= 70]
    if exact:
        return exact[:2], "품명/규격 텍스트 매칭"

    ks_code, grade, diameter = SUPPORTED_MATERIALS[group_name]["representative"]
    representative = next(
        (
            material
            for material in materials
            if material.ks_code == ks_code and material.ks_grade == grade and material.diameter == diameter
        ),
        None,
    )
    return ([representative] if representative else materials[:1]), "대표 규격 매핑"


def parse_date(value) -> date | None:
    digits = re.sub(r"[^0-9]", "", str(value or ""))[:8]
    if len(digits) != 8:
        return None
    try:
        return datetime.strptime(digits, "%Y%m%d").date()
    except ValueError:
        return None


def parse_decimal(value) -> Decimal | None:
    cleaned = re.sub(r"[^0-9.-]", "", str(value or ""))
    if not cleaned:
        return None
    try:
        parsed = Decimal(cleaned)
        return parsed if parsed >= 0 else None
    except InvalidOperation:
        return None


def supplier_key(item: dict) -> str:
    raw = re.sub(
        r"[^0-9A-Za-z]",
        "",
        str(item.get("cntrctCorpNo") or item.get("cntrctCorpBizno") or ""),
    )
    if raw:
        return raw[:20]
    name = str(item.get("cntrctCorpNm") or "").strip()
    return f"SM-{hashlib.sha1(name.encode('utf-8')).hexdigest()[:16]}"


def geocode_address(address: str) -> tuple[float | None, float | None]:
    if not address or not KAKAO_REST_API_KEY:
        return None, None
    try:
        response = requests.get(
            KAKAO_GEOCODE_URL,
            params={"query": address},
            headers={"Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"},
            timeout=10,
        )
        response.raise_for_status()
        documents = response.json().get("documents") or []
        if documents:
            return float(documents[0]["y"]), float(documents[0]["x"])
    except (requests.RequestException, ValueError, KeyError):
        pass
    return None, None


def upsert_supplier(item: dict) -> Supplier | None:
    name = str(item.get("cntrctCorpNm") or "").strip()
    if not name:
        return None
    address = str(item.get("fctryLocplc") or item.get("hdoffceLocplc") or "").strip()
    supplier, created = Supplier.objects.get_or_create(
        business_no=supplier_key(item),
        defaults={"name": name, "address": address, "source": "narajangteo"},
    )
    changed = []
    if supplier.name != name:
        supplier.name = name
        changed.append("name")
    if address and not supplier.address:
        supplier.address = address
        changed.append("address")
    if address and not supplier.has_coordinates:
        latitude, longitude = geocode_address(address)
        if latitude is not None and longitude is not None:
            supplier.latitude = latitude
            supplier.longitude = longitude
            changed.extend(("latitude", "longitude"))
    if changed:
        supplier.save(update_fields=list(dict.fromkeys(changed)))
    return supplier


def save_history(
    supplier: Supplier,
    material: Material,
    item: dict,
    match_basis: str,
    relevance_basis: str,
    operation: str,
    subtype: str,
) -> bool:
    contract_date = parse_date(item.get("cntrctDate") or item.get("cntrctBgnDate"))
    unit_price = parse_decimal(item.get("cntrctPrceAmt") or item.get("orderCalclPrceAmt"))
    quantity = parse_decimal(item.get("remndrQty"))
    if not contract_date or unit_price is None or unit_price <= 0:
        return False

    raw_data = dict(item)
    raw_data.update(
        {
            "source": "나라장터 종합쇼핑몰 API",
            "shoppingMallOperation": operation,
            "paceflowMatchBasis": match_basis,
            "paceflowRelevanceBasis": relevance_basis,
            "paceflowMaterialSubtype": subtype,
        }
    )
    _, created = SupplyHistory.objects.get_or_create(
        supplier=supplier,
        material=material,
        contract_date=contract_date,
        unit_price=unit_price,
        defaults={"quantity": quantity, "raw_data": raw_data},
    )
    return created


def main() -> None:
    parser = argparse.ArgumentParser(description="종합쇼핑몰 형강·강재 및 전기 배관재 수집")
    parser.add_argument("--materials", default="형강·강재,전기 배관재", help="쉼표로 구분")
    parser.add_argument("--operation", choices=sorted(OPERATIONS), default="registered")
    parser.add_argument("--start-page", type=int, default=1, help="수집 시작 페이지")
    parser.add_argument("--pages", type=int, default=0, help="0이면 시작 페이지부터 끝까지")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--preview-limit", type=int, default=20)
    args = parser.parse_args()

    if not API_KEY:
        parser.error("SHOPPING_MALL_API_KEY가 .env에 없습니다.")
    requested = {
        MATERIAL_ALIASES.get(name.strip(), name.strip())
        for name in args.materials.split(",")
        if name.strip()
    }
    unsupported = requested - set(SUPPORTED_MATERIALS)
    if unsupported:
        parser.error(f"지원하지 않는 자재: {', '.join(sorted(unsupported))}")
    if args.start_page < 1:
        parser.error("--start-page는 1 이상이어야 합니다.")

    operation = OPERATIONS[args.operation]
    first_items, total_count = parse_page(fetch_page(operation, args.start_page))
    total_pages = math.ceil(total_count / API_PAGE_SIZE) if total_count else 1
    if args.start_page > total_pages:
        parser.error(f"--start-page가 전체 페이지 수({total_pages})보다 큽니다.")
    end_page = (
        min(total_pages, args.start_page + args.pages - 1)
        if args.pages > 0
        else total_pages
    )
    pages_to_scan = end_page - args.start_page + 1
    print(
        f"{args.operation} 품목 {total_count}건 / {args.start_page}-{end_page}페이지 검사 / "
        f"예상 API 호출 {pages_to_scan}회"
    )

    seen_products = set()
    matched = saved = skipped = failed_pages = 0

    def process_items(items: list[dict]) -> None:
        nonlocal matched, saved, skipped
        for item in items:
            product_key = str(item.get("prdctIdntNo") or item.get("shopngCntrctNo") or "")
            if product_key and product_key in seen_products:
                continue
            if product_key:
                seen_products.add(product_key)

            material_name, group_name, subtype, relevance_basis = detect_material(item, requested)
            if not material_name:
                continue
            materials, match_basis = choose_materials(item, material_name, group_name, subtype)
            if not materials:
                skipped += 1
                continue
            matched += 1

            if args.dry_run:
                if matched <= args.preview_limit:
                    print(
                        f"  [미리보기] {group_name}/{subtype} | {item.get('cntrctCorpNm') or '공급사 미확인'} | "
                        f"{item.get('prdctClsfcNoNm') or item.get('prdctSpecNm') or '품명 미확인'} | "
                        f"{', '.join(str(material) for material in materials)}"
                    )
                continue

            supplier = upsert_supplier(item)
            if not supplier:
                skipped += 1
                continue
            for material in materials:
                saved += int(
                    save_history(
                        supplier,
                        material,
                        item,
                        match_basis,
                        relevance_basis,
                        operation,
                        subtype,
                    )
                )

    process_items(first_items)
    completed_pages = 1
    if pages_to_scan > 1:
        with ThreadPoolExecutor(max_workers=max(1, min(args.workers, 8))) as executor:
            futures = {
                executor.submit(fetch_page, operation, page): page
                for page in range(args.start_page + 1, end_page + 1)
            }
            for future in as_completed(futures):
                page = futures[future]
                try:
                    process_items(parse_page(future.result())[0])
                except ApiRateLimitError:
                    failed_pages += 1
                    for pending in futures:
                        pending.cancel()
                    print("API 호출 한도에 도달해 남은 페이지 검사를 중단합니다.")
                    break
                except RuntimeError as exc:
                    failed_pages += 1
                    print(f"  페이지 {page} 제외: {exc}")
                completed_pages += 1
                if completed_pages % 20 == 0 or completed_pages == pages_to_scan:
                    print(f"진행 {completed_pages}/{pages_to_scan}페이지 / 매칭 {matched}건")

    mode = "미리보기" if args.dry_run else "수집"
    print(
        f"{mode} 완료: 매칭 품목 {matched}건 / 신규 이력 {saved}건 / "
        f"저장 제외 {skipped}건 / API 실패 {failed_pages}페이지"
    )


if __name__ == "__main__":
    main()
