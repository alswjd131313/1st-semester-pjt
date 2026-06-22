# -*- coding: utf-8 -*-
"""
나라장터 계약정보 수집 스크립트
오퍼레이션: getCntrctInfoListThngPPSSrch (3번 - 품명 검색)
실행: python scripts/collect_narajangteo.py --material 철근 --year 2025
"""

import os
import sys
import argparse
import re
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

TEXT_FIELDS = (
    "prdctClsfcNoNm",
    "prdctIdntNoNm",
    "cntrctPrdctNm",
    "cntrctNm",
    "baseDtls",
    "pubPrcrmntClsfcNm",
    "pubPrcrmntLrgClsfcNm",
    "pubPrcrmntMidClsfcNm",
)

REPRESENTATIVE_MATERIALS = {
    "철근": ("KS D 3504", "SD400", "D13"),
    "H빔": ("KS D 3503", "SS275", "H-300x300"),
    "시멘트": ("KS L 5201", "1종", "40kg 포대"),
    "단열재": ("KS M ISO 4898", "XPS II B-1", "50T"),
    "전선관": ("KS C IEC 61386-1", "경질 합성수지관", "16C"),
}

DEFAULT_SEARCH_KEYWORDS = {
    "철근": ("철근", "이형철근"),
    "H빔": ("H형강", "H빔"),
    "시멘트": ("시멘트", "포틀랜드시멘트"),
    "단열재": ("단열재", "보온재"),
    "전선관": ("전선관", "합성수지제전선관", "가요전선관"),
}

MATERIAL_RELEVANCE_KEYWORDS = {
    "철근": ("철근", "이형철근", "봉강", "REBAR"),
    "H빔": ("H빔", "H형강", "에이치빔"),
    "시멘트": ("시멘트", "포틀랜드"),
    "단열재": (
        "단열재",
        "보온재",
        "압출법",
        "비드법",
        "발포폴리스티렌",
        "폴리우레탄폼",
        "페놀폼",
        "XPS",
        "EPS",
    ),
    "전선관": (
        "전선관",
        "합성수지제전선관",
        "합성수지관",
        "가요전선관",
        "PVC전선관",
        "CD관",
        "PF관",
    ),
}

MATERIAL_UNSUPPORTED_KEYWORDS = {
    "시멘트": ("슬래그시멘트", "고로슬래그", "플라이애시시멘트"),
    "단열재": ("글라스울", "섬유단열재", "진공단열재", "미네랄울"),
}


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


def normalize_text(value: str) -> str:
    return re.sub(r"[^0-9A-Z가-힣]", "", str(value or "").upper())


def build_contract_text(item: dict) -> str:
    return " ".join(str(item.get(field, "")) for field in TEXT_FIELDS if item.get(field))


def evaluate_material_relevance(item: dict, material_name: str) -> tuple[bool, str]:
    text = normalize_text(build_contract_text(item))
    keywords = MATERIAL_RELEVANCE_KEYWORDS.get(material_name, (material_name,))
    matched_keyword = next(
        (keyword for keyword in keywords if normalize_text(keyword) in text),
        None,
    )

    if not matched_keyword:
        return False, f"{material_name} 관련 품명·규격 없음"

    unsupported_keyword = next(
        (
            keyword
            for keyword in MATERIAL_UNSUPPORTED_KEYWORDS.get(material_name, ())
            if normalize_text(keyword) in text
        ),
        None,
    )
    if unsupported_keyword:
        return False, f"현재 지원 규격 외 타입: {unsupported_keyword}"

    basis = f"자재 키워드 확인: {matched_keyword}"
    item["_paceflow_relevance_basis"] = basis
    return True, basis


def material_match_score(material: Material, item: dict) -> int:
    text = normalize_text(build_contract_text(item))
    grade = normalize_text(material.ks_grade)
    size = normalize_text(material.diameter)
    score = 0

    if grade and grade in text:
        score += 50
    if size and size in text:
        score += 70

    if material.name == "시멘트":
        cement_hints = {
            "1종": ("1종", "보통", "벌크"),
            "2종": ("2종", "중용열"),
            "3종": ("3종", "조강"),
            "4종": ("4종", "저열"),
            "5종": ("5종", "내황산염"),
        }
        if any(normalize_text(hint) in text for hint in cement_hints.get(material.ks_grade, ())):
            score += 80

    if material.name == "단열재":
        insulation_hints = {
            "EPS": ("EPS", "발포폴리스티렌"),
            "XPS": ("XPS", "압출법", "압출보온"),
            "PUR": ("PUR", "우레탄", "폴리우레탄"),
            "PF": ("PF", "페놀폼", "페놀"),
            "셀룰로오스": ("셀룰로오스",),
        }
        for family, hints in insulation_hints.items():
            if family in normalize_text(material.ks_grade) and any(normalize_text(hint) in text for hint in hints):
                score += 80

    if material.name == "전선관":
        if "가요" in text and "가요" in material.ks_grade:
            score += 80
        if any(token in text for token in ("경질", "합성수지", "PVC")) and "경질" in material.ks_grade:
            score += 80

    if material.name == "H빔":
        h_size = material.diameter.replace("H-", "")
        if normalize_text(h_size) in text:
            score += 70

    return score


def choose_materials(materials, item: dict, material_name: str) -> list[Material]:
    material_list = list(materials)
    scored = [
        (material_match_score(material, item), material)
        for material in material_list
    ]
    exact_matches = [material for score, material in scored if score >= 70]

    if exact_matches:
        return exact_matches[:2]

    representative = REPRESENTATIVE_MATERIALS.get(material_name)
    if representative:
        ks_code, ks_grade, diameter = representative
        for material in material_list:
            if (
                material.ks_code == ks_code
                and material.ks_grade == ks_grade
                and material.diameter == diameter
            ):
                item["_paceflow_match_basis"] = "대표 규격 매핑"
                return [material]

    item["_paceflow_match_basis"] = "세부 규격 미확인"
    return material_list[:1]


def print_dry_run_preview(corp: dict, item: dict, matched_materials) -> None:
    supplier_name = corp.get("name", "업체명 미확인")
    contract_name = (
        item.get("cntrctPrdctNm")
        or item.get("prdctIdntNoNm")
        or item.get("cntrctNm")
        or "계약명 미확인"
    )
    material_labels = ", ".join(str(material) for material in matched_materials)
    match_basis = item.get("_paceflow_match_basis", "품명/규격 텍스트 매칭")
    contract_date = item.get("cntrctCnclsDate", "날짜 미확인")
    print(
        f"  [미리보기] {supplier_name} | {contract_name} | "
        f"{material_labels} | {match_basis} | {contract_date}"
    )


def print_dry_run_exclusion(item: dict, reason: str) -> None:
    contract_name = (
        item.get("cntrctPrdctNm")
        or item.get("prdctIdntNoNm")
        or item.get("cntrctNm")
        or "계약명 미확인"
    )
    print(f"  [제외] {contract_name} | {reason}")


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
        raw_data = dict(item)
        raw_data["paceflowMatchBasis"] = item.get("_paceflow_match_basis", "품명/규격 텍스트 매칭")
        raw_data["paceflowRelevanceBasis"] = item.get("_paceflow_relevance_basis", "")
        _, created = SupplyHistory.objects.get_or_create(
            supplier=supplier,
            material=material,
            contract_date=contract_date,
            unit_price=unit_price,
            defaults={"raw_data": raw_data},
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
    parser.add_argument("--search", help="검색어. 여러 개는 쉼표로 구분하며 생략하면 자재별 기본 검색어 사용")
    parser.add_argument("--year",     type=int, default=2025)
    parser.add_argument("--years", help="수집 연도. 여러 개는 쉼표로 구분 (예: 2024,2025,2026)")
    parser.add_argument("--pages",    type=int, default=5)
    parser.add_argument("--dry-run", action="store_true", help="DB 저장 없이 매칭 결과만 확인")
    args = parser.parse_args()
    search_keywords = (
        [keyword.strip() for keyword in args.search.split(",") if keyword.strip()]
        if args.search
        else list(DEFAULT_SEARCH_KEYWORDS.get(args.material, (args.material,)))
    )
    try:
        years = (
            [int(year.strip()) for year in args.years.split(",") if year.strip()]
            if args.years
            else [args.year]
        )
    except ValueError:
        parser.error("--years는 2024,2025처럼 숫자와 쉼표로 입력하세요.")

    if not NARAJANGTEO_KEY:
        print("❌ NARAJANGTEO_API_KEY가 .env에 없습니다.")
        sys.exit(1)

    materials = Material.objects.filter(name__icontains=args.material)
    if not materials.exists():
        print(f"❌ '{args.material}' 자재가 DB에 없습니다. seed_data.py를 먼저 실행하세요.")
        sys.exit(1)

    mode_label = "미리보기" if args.dry_run else "수집"
    print(
        f"\n{mode_label} 시작: {args.material} / 검색어 {', '.join(search_keywords)} / "
        f"연도 {', '.join(map(str, years))} / 최대 {len(search_keywords) * len(years) * args.pages * 10}건\n"
    )

    total_saved = 0
    total_previewed = 0
    total_matched = 0
    total_excluded = 0

    for year in years:
        for search_keyword in search_keywords:
            for page in range(1, args.pages + 1):
                print(f"{year}년 / {search_keyword} / 페이지 {page} 수집 중...")
                try:
                    data = fetch_contracts(search_keyword, year, page)
                    items = parse_contracts(data)
                except Exception as e:
                    print(f"  ❌ API 오류: {e}")
                    break

                if not items:
                    print("  더 이상 데이터 없음. 다음 검색으로 이동.")
                    break

                for item in items:
                    is_relevant, relevance_reason = evaluate_material_relevance(item, args.material)
                    if not is_relevant:
                        total_excluded += 1
                        if args.dry_run:
                            print_dry_run_exclusion(item, relevance_reason)
                        continue

                    corp_list_str = item.get("corpList", "")
                    address = item.get("cntrctInsttNm", "")  # 계약기관명 (주소 대용)
                    corps = parse_corp_list(corp_list_str)
                    if not corps:
                        continue

                    # 주계약업체만 저장
                    main_corp = corps[0]
                    matched_materials = choose_materials(materials, item, args.material)

                    if args.dry_run:
                        print_dry_run_preview(main_corp, item, matched_materials)
                        total_previewed += 1
                        total_matched += len(matched_materials)
                        continue

                    supplier = upsert_supplier(main_corp, address)
                    if not supplier:
                        continue

                    for material in matched_materials:
                        if save_history(supplier, material, item):
                            total_saved += 1
                            print(f"  ✓ 저장: {supplier.name} / {material} / {item.get('cntrctCnclsDate')}")

    if args.dry_run:
        print(
            f"\n미리보기 완료: 계약 {total_previewed}건, "
            f"자재 매칭 {total_matched}건, 제외 {total_excluded}건 (DB 저장 없음)"
        )
    else:
        print(f"\n✅ 완료: 총 {total_saved}건 저장, 부적합 계약 {total_excluded}건 제외")


if __name__ == "__main__":
    main()
