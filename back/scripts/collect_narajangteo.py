# -*- coding: utf-8 -*-
"""
나라장터 철근 계약 수집 스크립트
실행: python scripts/collect_narajangteo.py

수정 사항:
- URL HTTP로 변경 (HTTPS는 타임아웃)
- Kakao 키워드 검색으로 공급사 좌표 획득 (API에 주소 필드 없음)
- 날짜 범위를 분할해서 페이지 타임아웃 방지
"""

import os
import sys
import time
import requests
import django
from datetime import date, timedelta
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.conf import settings
from core.models import Material, Supplier, SupplyHistory

# ── API 설정
NARAJANGTEO_URL = (
    "http://apis.data.go.kr/1230000/ao/CntrctInfoService"
    "/getCntrctInfoListThngPPSSrch"
)
KAKAO_KEYWORD_URL = "https://dapi.kakao.com/v2/local/search/keyword.json"

NARAJANGTEO_KEY = os.getenv("NARAJANGTEO_API_KEY", "")
KAKAO_KEY = getattr(settings, "KAKAO_REST_API_KEY", "")


# ──────────────────────────────────────────
# 1. 나라장터 계약 수집
# ──────────────────────────────────────────

def fetch_contracts(start: str, end: str, page: int = 1, rows: int = 100) -> dict:
    """YYYYMMDD 형식 날짜 범위로 철근 계약 조회"""
    kw = quote("철근", encoding="utf-8")
    url = (
        f"{NARAJANGTEO_URL}"
        f"?ServiceKey={NARAJANGTEO_KEY}"
        f"&numOfRows={rows}&pageNo={page}"
        f"&inqryDiv=1"
        f"&inqryBgnDate={start}&inqryEndDate={end}"
        f"&prdctClsfcNoNm={kw}"
        f"&type=json"
    )
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()


def parse_contracts(data: dict) -> tuple[int, list]:
    body = data.get("response", {}).get("body", {})
    total = int(body.get("totalCount", 0))
    items = body.get("items", [])
    if isinstance(items, dict):
        item = items.get("item", [])
        items = item if isinstance(item, list) else [item]
    return total, items or []


# ──────────────────────────────────────────
# 2. corpList 파싱
# 형식: [순번^업체구분^공동도급방식^업체명^대표자^국적^지분율^채권자명^담당자^사업자번호]
# ──────────────────────────────────────────

def parse_corp_list(corp_str: str) -> list[dict]:
    if not corp_str:
        return []
    corps = []
    for entry in corp_str.strip("[]").split("],["):
        parts = entry.split("^")
        name    = parts[3].strip() if len(parts) > 3 else ""
        biz_no  = parts[-1].strip() if parts else ""
        if name:
            corps.append({"name": name, "biz_no": biz_no})
    return corps


# ──────────────────────────────────────────
# 3. Kakao 키워드 검색으로 공급사 좌표 획득
# ──────────────────────────────────────────

def normalize_name(name: str) -> str:
    """비교용 회사명 정제"""
    for s in ["주식회사", "(주)", "유한회사", "(유)", "주식회사 "]:
        name = name.replace(s, "")
    return name.strip()


def find_coords_by_name(company_name: str) -> tuple[float | None, float | None, str]:
    """Kakao 키워드 검색으로 공급사 위경도 획득"""
    if not KAKAO_KEY:
        return None, None, ""

    clean = normalize_name(company_name)
    queries = [f"{clean} 철강", f"{clean} 철근", f"{clean} 건자재", clean]

    headers = {"Authorization": f"KakaoAK {KAKAO_KEY}"}
    for q in queries:
        try:
            resp = requests.get(
                KAKAO_KEYWORD_URL,
                headers=headers,
                params={"query": q, "size": 3},
                timeout=5,
            )
            docs = resp.json().get("documents", [])
            for doc in docs:
                found = normalize_name(doc.get("place_name", ""))
                # 검색 결과 이름이 회사명과 일치하는지 간단 확인
                if clean[:4] in found or found[:4] in clean:
                    return float(doc["y"]), float(doc["x"]), doc.get("address_name", "")
        except Exception:
            pass
        time.sleep(0.05)

    return None, None, ""


# ──────────────────────────────────────────
# 4. 공급사 upsert
# ──────────────────────────────────────────

def upsert_supplier(name: str, biz_no: str) -> Supplier | None:
    if not name:
        return None

    key = biz_no if biz_no else f"nara_{name}"

    supplier, created = Supplier.objects.get_or_create(
        business_no=key,
        defaults={"name": name, "source": "narajangteo"},
    )

    if created or not supplier.has_coordinates:
        lat, lng, addr = find_coords_by_name(name)
        if lat and lng:
            supplier.latitude  = lat
            supplier.longitude = lng
            if addr:
                supplier.address = addr
            supplier.save(update_fields=["latitude", "longitude", "address"])
            print(f"    위치 등록: {name} ({addr[:30]})")
        else:
            print(f"    위치 미확인: {name}")

    return supplier


# ──────────────────────────────────────────
# 5. 납품 이력 저장
# ──────────────────────────────────────────

def save_history(supplier: Supplier, material: Material, item: dict) -> bool:
    raw_date  = item.get("cntrctCnclsDate", "")
    raw_price = item.get("thtmCntrctAmt", 0)

    try:
        from datetime import datetime
        contract_date = datetime.strptime(raw_date[:10], "%Y-%m-%d").date()
        unit_price    = float(str(raw_price).replace(",", "") or 0)
    except (ValueError, TypeError):
        return False

    if unit_price <= 0:
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
    except Exception:
        return False


# ──────────────────────────────────────────
# 6. 날짜 범위 분할
# ──────────────────────────────────────────

def date_chunks(year_start: int, year_end: int, chunk_days: int = 30):
    """연도 범위를 chunk_days 단위로 분할"""
    cur = date(year_start, 1, 1)
    end = date(year_end, 12, 31)
    while cur <= end:
        nxt = min(cur + timedelta(days=chunk_days - 1), end)
        yield cur.strftime("%Y%m%d"), nxt.strftime("%Y%m%d")
        cur = nxt + timedelta(days=1)


# ──────────────────────────────────────────
# 7. 메인
# ──────────────────────────────────────────

def main():
    if not NARAJANGTEO_KEY:
        print("NARAJANGTEO_API_KEY가 .env에 없습니다.")
        sys.exit(1)

    materials = list(Material.objects.filter(name__icontains="철근"))
    if not materials:
        print("철근 자재가 DB에 없습니다. seed_data.py를 먼저 실행하세요.")
        sys.exit(1)

    print(f"연결된 자재: {len(materials)}개")
    print(f"수집 범위: 2024~2025년 (월 단위 분할)\n")

    total_contracts = 0
    total_suppliers = 0
    total_histories = 0

    for start, end in date_chunks(2024, 2025, chunk_days=30):
        print(f"[{start}~{end}] 수집 중...")
        try:
            data = fetch_contracts(start, end, page=1, rows=100)
            total_count, items = parse_contracts(data)
        except Exception as e:
            print(f"  API 오류: {e}")
            time.sleep(2)
            continue

        if not items:
            print(f"  결과 없음 (전체 {total_count}건)")
            continue

        print(f"  {total_count}건 중 {len(items)}건 처리")
        total_contracts += len(items)

        for item in items:
            corps = parse_corp_list(item.get("corpList", ""))
            if not corps:
                continue

            corp = corps[0]  # 주계약업체만
            supplier = upsert_supplier(corp["name"], corp["biz_no"])
            if not supplier:
                continue

            if supplier.pk and not hasattr(supplier, "_counted"):
                total_suppliers += 1
                supplier._counted = True

            for material in materials:
                if save_history(supplier, material, item):
                    total_histories += 1

        time.sleep(0.3)

    print()
    print(f"완료:")
    print(f"  처리된 계약: {total_contracts}건")
    print(f"  공급사: {Supplier.objects.filter(source='narajangteo').count()}개")
    print(f"  좌표 있는 공급사: {Supplier.objects.exclude(latitude=None).count()}개")
    print(f"  납품이력 추가: {total_histories}건")


if __name__ == "__main__":
    main()
