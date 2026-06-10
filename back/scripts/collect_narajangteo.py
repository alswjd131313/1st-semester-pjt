# -*- coding: utf-8 -*-
"""
나라장터 계약정보 수집 스크립트
오퍼레이션: getCntrctInfoListThngPPSSrch (3번 - 품명 검색)
실행: python scripts/collect_narajangteo.py --material 철근 --year 2025
"""

import os
import sys
import argparse
import requests
import django
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from core.models import Material, Supplier, SupplyHistory

# ── PDF 기준 정확한 URL (ao 경로 포함)
BASE_URL = "https://apis.data.go.kr/1230000/ao/CntrctInfoService/getCntrctInfoListThngPPSSrch"

NARAJANGTEO_KEY = os.getenv("NARAJANGTEO_API_KEY", "")
JUSO_KEY        = os.getenv("JUSO_API_KEY", "")
JUSO_URL        = "https://business.juso.go.kr/addrlink/addrCoordApi.do"


# ──────────────────────────────────────────
# 1. 나라장터 계약 이력 수집
# ──────────────────────────────────────────

def fetch_contracts(material_name: str, year: int, page: int = 1) -> dict:
    params = {
        "ServiceKey":      NARAJANGTEO_KEY,
        "numOfRows":       10,
        "pageNo":          page,
        "inqryDiv":        "1",
        "inqryBgnDate":    f"{year}0101",
        "inqryEndDate":    f"{year}1231",
        "prdctClsfcNoNm":  material_name,
        "type":            "json",
    }

    for attempt in range(3):  # 최대 3번 재시도
        try:
            res = requests.get(BASE_URL, params=params, timeout=60)
            res.raise_for_status()
            return res.json()
        except requests.exceptions.Timeout:
            print(f"  ⏱ 타임아웃 ({attempt+1}/3) 재시도 중...")
            import time
            time.sleep(3)
        except Exception as e:
            raise e

    raise Exception("3번 재시도 모두 실패")


def parse_contracts(data: dict) -> list[dict]:
    try:
        body  = data.get("response", {}).get("body", {})
        total = body.get("totalCount", 0)
        print(f"  전체 결과 수: {total}건")
        items = body.get("items", [])

        if not items:
            return []
        if isinstance(items, list):       # ← 이 경우가 실제 응답
            return items
        if isinstance(items, dict):       # 혹시 단건일 때 대비
            item = items.get("item", [])
            return item if isinstance(item, list) else [item]
        return []
    except Exception as e:
        print(f"  파싱 오류: {e}")
        return []


# ──────────────────────────────────────────
# 2. corpList 파싱
# corpList 형식: [순번^업체구분^공동도급방식^업체명^대표자명^국적^지분율^채권자명^담당자^사업자번호]
# ──────────────────────────────────────────

def parse_corp_list(corp_list_str: str) -> list[dict]:
    corps = []
    if not corp_list_str:
        return corps

    entries = corp_list_str.strip("[]").split("],[")
    for entry in entries:
        parts = entry.split("^")
        name        = parts[3].strip() if len(parts) > 3 else ""
        business_no = parts[-1].strip()  # ← 마지막 인덱스가 항상 사업자번호

        if name:
            corps.append({"name": name, "business_no": business_no})
    return corps


# ──────────────────────────────────────────
# 3. 주소 → 좌표 변환
# ──────────────────────────────────────────

def address_to_coordinates(address: str):
    if not address or not JUSO_KEY:
        return None, None
    try:
        res = requests.get(JUSO_URL, params={
            "confmKey":   JUSO_KEY,
            "keyword":    address,
            "resultType": "json",
        }, timeout=5)
        juso = res.json().get("results", {}).get("juso", [])
        if juso:
            return float(juso[0]["entX"]), float(juso[0]["entY"])
    except Exception as e:
        print(f"  ⚠ 좌표 변환 실패 ({address}): {e}")
    return None, None


# ──────────────────────────────────────────
# 4. 공급사 upsert
# ──────────────────────────────────────────

def upsert_supplier(corp: dict, address: str = "") -> Supplier | None:
    name        = corp.get("name", "").strip()
    business_no = corp.get("business_no", "").strip()

    if not name:
        return None

    key = business_no if business_no else f"unknown_{name}"

    supplier, created = Supplier.objects.get_or_create(
        business_no=key,
        defaults={
            "name":    name,
            "address": address,
            "source":  "narajangteo",
        },
    )

    if created or not supplier.has_coordinates:
        if address:
            lng, lat = address_to_coordinates(address)
            if lat and lng:
                supplier.latitude  = lat
                supplier.longitude = lng
                supplier.save(update_fields=["latitude", "longitude"])
                print(f"    📍 좌표 등록: {name}")

    return supplier


# ──────────────────────────────────────────
# 5. 납품 이력 저장
# ──────────────────────────────────────────

def save_history(supplier: Supplier, material: Material, item: dict) -> bool:
    from datetime import datetime

    raw_date  = item.get("cntrctCnclsDate", "")
    raw_price = item.get("thtmCntrctAmt", 0)

    try:
        contract_date = datetime.strptime(raw_date[:10], "%Y-%m-%d").date()
        unit_price    = float(str(raw_price).replace(",", "") or 0)
    except (ValueError, TypeError) as e:
        print(f"    ⚠ 날짜/가격 파싱 실패: {e} / date={raw_date} price={raw_price}")
        return False

    if unit_price <= 0:
        print(f"    ⚠ 단가 0 스킵: {raw_price}")
        return False

    try:
        _, created = SupplyHistory.objects.get_or_create(
            supplier=supplier,
            material=material,
            contract_date=contract_date,
            unit_price=unit_price,
            defaults={"raw_data": item},
        )
        return created
    except Exception as e:
        print(f"    ❌ DB 저장 실패: {e}")
        return False


# ──────────────────────────────────────────
# 6. 메인
# ──────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="나라장터 계약 이력 수집")
    parser.add_argument("--material", required=True, help="자재명 (예: 철근)")
    parser.add_argument("--year",     type=int, default=2025)
    parser.add_argument("--pages",    type=int, default=5)
    args = parser.parse_args()

    if not NARAJANGTEO_KEY:
        print("❌ NARAJANGTEO_API_KEY가 .env에 없습니다.")
        sys.exit(1)

    materials = Material.objects.filter(name__icontains=args.material)
    if not materials.exists():
        print(f"❌ '{args.material}' 자재가 DB에 없습니다. seed_data.py를 먼저 실행하세요.")
        sys.exit(1)

    print(f"\n수집 시작: {args.material} / {args.year}년 / 최대 {args.pages * 100}건\n")

    total_saved = 0

    for page in range(1, args.pages + 1):
        print(f"페이지 {page} 수집 중...")
        try:
            data  = fetch_contracts(args.material, args.year, page)
            items = parse_contracts(data)
        except Exception as e:
            print(f"  ❌ API 오류: {e}")
            break

        if not items:
            print("  더 이상 데이터 없음. 종료.")
            break

        for item in items:
            corp_list_str = item.get("corpList", "")
            address       = item.get("cntrctInsttNm", "")  # 계약기관명 (주소 대용)

            corps = parse_corp_list(corp_list_str)
            if not corps:
                continue

            # 주계약업체만 저장
            main_corp = corps[0]
            supplier  = upsert_supplier(main_corp, address)
            if not supplier:
                continue

            for material in materials:
                if save_history(supplier, material, item):
                    total_saved += 1
                    print(f"  ✓ 저장: {supplier.name} / {material} / {item.get('cntrctCnclsDate')}")

    print(f"\n✅ 완료: 총 {total_saved}건 납품 이력 저장됨")


if __name__ == "__main__":
    main()