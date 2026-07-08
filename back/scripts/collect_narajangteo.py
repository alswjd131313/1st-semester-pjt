# -*- coding: utf-8 -*-
"""
나라장터 계약정보 수집 스크립트
오퍼레이션: getCntrctInfoListThngPPSSrch (3번 - 품명 검색)
실행: python scripts/collect_narajangteo.py --material 철근 --year 2025
"""

import os
import sys
import argparse
import hashlib
import re
import time
from collections import Counter
from decimal import Decimal, InvalidOperation
import requests
import django
from datetime import date, datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from core.models import CategoryContractHistory, Material, Supplier, SupplyHistory

# ── PDF 기준 정확한 URL (ao 경로 포함)
BASE_URL = "https://apis.data.go.kr/1230000/ao/CntrctInfoService/getCntrctInfoListThngPPSSrch"

NARAJANGTEO_KEY = os.getenv("NARAJANGTEO_API_KEY", "")
JUSO_KEY        = os.getenv("JUSO_API_KEY", "") or os.getenv("JUSO_SEARCH_API_KEY", "")
JUSO_URL        = "https://business.juso.go.kr/addrlink/addrCoordApi.do"

DEFAULT_TIMEOUT_SECONDS = 20.0
DEFAULT_RETRIES = 2
DEFAULT_RETRY_SLEEP_SECONDS = 1.5

SUPPLIER_ADDRESS_FIELDS = (
    "cntrctCorpAddr",
    "corpAddr",
    "hdoffceLocplc",
    "fctryLocplc",
)

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

MATERIAL_COMPOSITE_KEYWORDS = {
    "철근": ("철근콘크리트관", "철근콘크리트블록", "암거블록", "조립식철근콘크리트"),
    "시멘트": ("레미콘", "몰탈", "모르타르", "보수재"),
    "단열재": ("샌드위치패널", "복합패널", "외장패널", "단열도어"),
}

MATERIAL_CATEGORY_CODES = {
    "철근": "rebar",
    "H빔": "shape_steel",
    "시멘트": "cement",
    "단열재": "insulation",
    "전선관": "electrical_conduit",
}

CATEGORY_HISTORY_HOLD_REASONS = {
    "두께 미확정",
    "등급 미확정",
    "등급 미확정으로 복수 KS 후보 발생",
    "복수 KS 후보 발생",
    "명시 규격과 일치하는 KS 후보 없음",
    "전선관 종류 미확정",
    "전선관 규격 미확정",
    "전선관 종류에 일치하는 내부 Material 없음",
    "명시 규격과 일치하는 전선관 후보 없음",
    "복수 전선관 규격 발생",
}


# ──────────────────────────────────────────
# 1. 나라장터 계약 이력 수집
# ──────────────────────────────────────────

class PageFetchError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        timed_out: bool,
        attempts: int,
        status_code: int | None = None,
        elapsed_seconds: float | None = None,
    ):
        super().__init__(message)
        self.timed_out = timed_out
        self.attempts = attempts
        self.status_code = status_code
        self.elapsed_seconds = elapsed_seconds


def fetch_contracts(
    material_name: str,
    start_date: date,
    end_date: date,
    page: int = 1,
    *,
    num_rows: int = 10,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    retries: int = DEFAULT_RETRIES,
    retry_sleep_seconds: float = DEFAULT_RETRY_SLEEP_SECONDS,
) -> dict:
    params = {
        "ServiceKey":      NARAJANGTEO_KEY,
        "numOfRows":       num_rows,
        "pageNo":          page,
        "inqryDiv":        "1",
        "inqryBgnDate":    start_date.strftime("%Y%m%d"),
        "inqryEndDate":    end_date.strftime("%Y%m%d"),
        "prdctClsfcNoNm":  material_name,
        "type":            "json",
    }

    total_attempts = retries + 1
    for attempt in range(1, total_attempts + 1):
        request_started = time.monotonic()
        try:
            res = requests.get(
                BASE_URL,
                params=params,
                timeout=(10, timeout_seconds),
            )
            res.raise_for_status()
            data = res.json()
            if isinstance(data, dict):
                data["_paceflow_fetch_meta"] = {
                    "attempts": attempt,
                    "retries_used": attempt - 1,
                    "recovered_after_timeout": attempt > 1,
                    "status_code": res.status_code,
                    "elapsed_seconds": time.monotonic() - request_started,
                }
            return data
        except requests.exceptions.Timeout as exc:
            if attempt < total_attempts:
                print(
                    f"  타임아웃: 키워드={material_name} 페이지={page} "
                    f"시도={attempt}/{total_attempts}, {retry_sleep_seconds:g}초 후 재시도"
                )
                time.sleep(retry_sleep_seconds)
                continue
            raise PageFetchError(
                f"read timeout ({timeout_seconds:g}초)",
                timed_out=True,
                attempts=attempt,
                elapsed_seconds=time.monotonic() - request_started,
            ) from exc
        except requests.RequestException as exc:
            raise PageFetchError(
                f"HTTP 요청 실패: {exc.__class__.__name__}",
                timed_out=False,
                attempts=attempt,
                status_code=getattr(getattr(exc, "response", None), "status_code", None),
                elapsed_seconds=time.monotonic() - request_started,
            ) from exc
        except ValueError as exc:
            raise PageFetchError(
                "JSON 응답 해석 실패",
                timed_out=False,
                attempts=attempt,
                status_code=res.status_code,
                elapsed_seconds=time.monotonic() - request_started,
            ) from exc

    raise PageFetchError("알 수 없는 API 실패", timed_out=False, attempts=total_attempts)


def response_diagnostics(data: dict, requested_page: int, requested_rows: int) -> dict:
    response = data.get("response")
    if not isinstance(response, dict):
        raise ValueError("response 객체 없음")
    header = response.get("header") or {}
    if not isinstance(header, dict):
        raise ValueError("response.header 형식 오류")
    body = response.get("body")
    if not isinstance(body, dict):
        raise ValueError("response.body 객체 없음")

    result_code = str(header.get("resultCode", ""))
    result_message = str(header.get("resultMsg", ""))
    if result_code and result_code != "00":
        raise ValueError(f"API 오류 code={result_code} message={result_message or '미확인'}")
    return {
        "result_code": result_code or "00",
        "result_message": result_message or "정상",
        "total_count": int(body.get("totalCount") or 0),
        "page_no": body.get("pageNo") or requested_page,
        "num_rows": body.get("numOfRows") or requested_rows,
    }


def parse_contracts(data: dict) -> list[dict]:
    body = data["response"]["body"]

    total = body.get("totalCount", 0)
    print(f"  전체 결과 수: {total}건")
    items = body.get("items", [])
    if not items:
        return []
    if isinstance(items, list):
        return [item for item in items if isinstance(item, dict)]
    if isinstance(items, dict):
        item = items.get("item", [])
        if isinstance(item, list):
            return [entry for entry in item if isinstance(entry, dict)]
        return [item] if isinstance(item, dict) else []
    raise ValueError("response.body.items 형식 오류")


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
    composite_keyword = next(
        (
            keyword
            for keyword in MATERIAL_COMPOSITE_KEYWORDS.get(material_name, ())
            if normalize_text(keyword) in text
        ),
        None,
    )
    if composite_keyword:
        return False, f"복합 제품 의심: {composite_keyword}"

    keywords = MATERIAL_RELEVANCE_KEYWORDS.get(material_name, (material_name,))
    matched_keyword = next(
        (keyword for keyword in keywords if normalize_text(keyword) in text),
        None,
    )

    if not matched_keyword:
        return False, "검색어와 품목 불일치"

    unsupported_keyword = next(
        (
            keyword
            for keyword in MATERIAL_UNSUPPORTED_KEYWORDS.get(material_name, ())
            if normalize_text(keyword) in text
        ),
        None,
    )
    if unsupported_keyword:
        return False, f"지원하지 않는 자재군: {unsupported_keyword}"

    if material_name == "전선관":
        raw_text = build_contract_text(item)
        normalized = normalize_text(raw_text)
        purchase_hints = ("구매", "구입", "납품", "지급자재", "관급자재", "제조구매")
        product_fields = " ".join(
            str(item.get(field, ""))
            for field in ("prdctClsfcNoNm", "prdctIdntNoNm", "cntrctPrdctNm")
            if item.get(field)
        )
        has_product_evidence = "전선관" in normalize_text(product_fields)
        if not has_product_evidence and not any(normalize_text(hint) in normalized for hint in purchase_hints):
            return False, "전선관 자체 구매 아님"

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


def extract_insulation_spec(item: dict) -> dict:
    raw_text = build_contract_text(item).upper()
    roman_text = raw_text.replace("Ⅱ", "II").replace("Ⅲ", "III")
    normalized = normalize_text(roman_text)

    family = next(
        (
            family
            for family, hints in {
                "PF": ("PF", "PF보드", "페놀폼", "페놀"),
                "XPS": ("XPS", "압출법", "압출보온"),
                "EPS": ("EPS", "비드법", "발포폴리스티렌"),
                "PUR": ("PUR", "폴리우레탄", "우레탄"),
            }.items()
            if any(normalize_text(hint) in normalized for hint in hints)
        ),
        None,
    )

    grade_type = None
    if re.search(r"(?<!I)III(?!I)|3\s*종", roman_text, re.IGNORECASE):
        grade_type = "III"
    elif re.search(r"(?<!I)II(?!I)|2\s*종", roman_text, re.IGNORECASE):
        grade_type = "II"

    grade_class = None
    class_match = re.search(r"\b([AB])\s*(?:등급|GRADE)\b", roman_text, re.IGNORECASE)
    if class_match:
        grade_class = class_match.group(1).upper()

    thickness_match = re.search(r"(?<!\d)(\d{1,3})\s*(?:T|MM|㎜)(?![A-Z0-9])", roman_text, re.IGNORECASE)
    thickness = f"{int(thickness_match.group(1))}T" if thickness_match else None
    return {
        "family": family,
        "grade_type": grade_type,
        "grade_class": grade_class,
        "thickness": thickness,
    }


def insulation_grade_type(grade: str) -> str | None:
    text = str(grade or "").upper().replace("Ⅱ", "II").replace("Ⅲ", "III")
    if re.search(r"(?<!I)III(?!I)", text):
        return "III"
    if re.search(r"(?<!I)II(?!I)", text):
        return "II"
    return None


def choose_insulation_materials(materials, item: dict) -> list[Material]:
    spec = extract_insulation_spec(item)
    family = spec["family"]
    grade_type = spec["grade_type"]
    thickness = spec["thickness"]

    if not family:
        item["_paceflow_hold_reason"] = "지원하지 않는 자재군"
        return []
    family_candidates = [
        material for material in materials
        if family in normalize_text(material.ks_grade)
    ]
    if not thickness:
        item["_paceflow_hold_reason"] = "두께 미확정"
        return []
    thickness_candidates = [
        material for material in family_candidates
        if normalize_text(material.diameter) == normalize_text(thickness)
    ]
    if not grade_type:
        if len(thickness_candidates) > 1:
            item["_paceflow_hold_reason"] = "등급 미확정으로 복수 KS 후보 발생"
        else:
            item["_paceflow_hold_reason"] = "등급 미확정"
        return []

    candidates = [
        material for material in thickness_candidates
        if insulation_grade_type(material.ks_grade) == grade_type
    ]
    if spec["grade_class"]:
        candidates = [
            material for material in candidates
            if re.search(
                rf"(?:^|\s){re.escape(spec['grade_class'])}(?:-|\s|$)",
                material.ks_grade,
                re.IGNORECASE,
            )
        ]
    if len(candidates) == 1:
        item["_paceflow_match_basis"] = (
            f"단열재 명시 규격 매핑: {family} {grade_type} {thickness}"
        )
        return candidates
    if len(candidates) > 1:
        item["_paceflow_hold_reason"] = "복수 KS 후보 발생"
    else:
        item["_paceflow_hold_reason"] = "명시 규격과 일치하는 KS 후보 없음"
    return []


def choose_conduit_materials(materials, item: dict) -> list[Material]:
    raw_text = build_contract_text(item).upper()
    normalized = normalize_text(raw_text)

    unsupported_family = next(
        (
            family
            for family in ("FEP", "ELP", "HI-VE", "HIVE")
            if normalize_text(family) in normalized
        ),
        None,
    )
    if unsupported_family:
        item["_paceflow_hold_reason"] = "전선관 종류에 일치하는 내부 Material 없음"
        item["_paceflow_detected_conduit_type"] = unsupported_family
        return []

    conduit_type = None
    subtype = None
    suffix = None
    type_label = None
    if "CD관" in normalized:
        conduit_type, subtype, suffix, type_label = "CD", "cd_conduit", "CD", "CD관"
    elif "PF관" in normalized:
        conduit_type, subtype, suffix, type_label = "PF", "pf_conduit", "PF", "PF관"
    elif "가요전선관" in normalized or "가요관" in normalized:
        conduit_type, subtype, suffix, type_label = "FLEXIBLE", "flexible_conduit", "F", "가요 전선관"
    elif "경질합성수지관" in normalized or "경질전선관" in normalized:
        conduit_type, subtype, suffix, type_label = "RIGID", "rigid_conduit", "C", "경질 합성수지관"

    if not conduit_type:
        item["_paceflow_hold_reason"] = "전선관 종류 미확정"
        return []

    size_matches = {
        int(match.group(1))
        for match in re.finditer(
            r"(?<!\d)(\d{1,3})\s*(?:CD|PF|MM|㎜|호|C|F)(?![A-Z0-9])",
            raw_text,
            re.IGNORECASE,
        )
    }
    if not size_matches:
        item["_paceflow_hold_reason"] = "전선관 규격 미확정"
        return []

    expected_diameters = {f"{size}{suffix}" for size in size_matches}
    candidates = [
        material
        for material in materials
        if material.material_subtype == subtype
        and material.diameter.upper() in expected_diameters
    ]
    if len(candidates) == 1:
        item["_paceflow_match_basis"] = (
            f"전선관 명시 규격 매핑: {type_label} {candidates[0].diameter}"
        )
        return candidates
    if len(candidates) > 1:
        item["_paceflow_hold_reason"] = "복수 전선관 규격 발생"
    else:
        item["_paceflow_hold_reason"] = "명시 규격과 일치하는 전선관 후보 없음"
    return []


def choose_materials(materials, item: dict, material_name: str) -> list[Material]:
    material_list = list(materials)
    if material_name == "단열재":
        return choose_insulation_materials(material_list, item)
    if material_name == "전선관":
        return choose_conduit_materials(material_list, item)
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


def supplier_business_key(corp: dict) -> str:
    name = str(corp.get("name", "")).strip()
    business_no = str(corp.get("business_no", "")).strip()
    return business_no or (f"unknown_{name}" if name else "")


def parse_history_identity(item: dict) -> tuple[object | None, Decimal | None, str]:
    raw_date = str(item.get("cntrctCnclsDate", ""))
    raw_price = str(item.get("thtmCntrctAmt", "")).replace(",", "").strip()
    try:
        contract_date = datetime.strptime(raw_date[:10], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None, None, "계약일 파싱 실패"
    try:
        unit_price = Decimal(raw_price or "0")
    except (InvalidOperation, ValueError, TypeError):
        return None, None, "계약금액 파싱 실패"
    if unit_price <= 0:
        return None, None, "유효 계약금액 없음"
    return contract_date, unit_price, ""


def contract_name_from_item(item: dict) -> str:
    return str(
        item.get("cntrctPrdctNm")
        or item.get("prdctIdntNoNm")
        or item.get("cntrctNm")
        or "계약명 미확인"
    ).strip()


def optional_decimal(value) -> Decimal | None:
    normalized = str(value or "").replace(",", "").strip()
    if not normalized:
        return None
    try:
        parsed = Decimal(normalized)
    except (InvalidOperation, ValueError, TypeError):
        return None
    return parsed if parsed >= 0 else None


def category_contract_external_id(corp: dict, item: dict) -> str:
    for field in (
        "untyCntrctNo",
        "cntrctNo",
        "cntrctRefNo",
        "bidNtceNo",
        "prdctIdntNo",
    ):
        value = str(item.get(field, "")).strip()
        if value:
            return value[:100]

    identity = "|".join([
        supplier_business_key(corp),
        contract_name_from_item(item),
        str(item.get("cntrctCnclsDate", ""))[:10],
        str(item.get("thtmCntrctAmt", "")).replace(",", "").strip(),
    ])
    return f"fallback-{hashlib.sha256(identity.encode('utf-8')).hexdigest()[:32]}"


def parse_category_history_identity(corp: dict, item: dict) -> tuple[dict | None, str]:
    raw_date = str(item.get("cntrctCnclsDate", ""))
    try:
        contract_date = datetime.strptime(raw_date[:10], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None, "계약일 파싱 실패"

    contract_name = contract_name_from_item(item)
    if not contract_name or contract_name == "계약명 미확인":
        return None, "계약명 없음"

    return {
        "contract_date": contract_date,
        "contract_name": contract_name,
        "unit_price": optional_decimal(item.get("thtmCntrctAmt")),
        "quantity": optional_decimal(
            item.get("cntrctQty")
            or item.get("thtmCntrctQty")
            or item.get("qty")
        ),
        "external_id": category_contract_external_id(corp, item),
    }, ""


def classify_dry_run_candidates(corp: dict, materials, item: dict) -> tuple[list[tuple[Material, str]], str]:
    key = supplier_business_key(corp)
    if not key:
        return [], "공급사 식별자 없음"

    contract_date, unit_price, error = parse_history_identity(item)
    if error:
        return [], error

    supplier = Supplier.objects.filter(business_no=key).first()
    classified = []
    for material in materials:
        is_duplicate = bool(
            supplier
            and SupplyHistory.objects.filter(
                supplier=supplier,
                material=material,
                contract_date=contract_date,
                unit_price=unit_price,
            ).exists()
        )
        classified.append((material, "duplicate" if is_duplicate else "new"))
    return classified, ""


def classify_category_history_candidate(corp: dict, material_category: str, item: dict) -> tuple[str, str]:
    if not material_category:
        return "", "자재군 코드 없음"
    key = supplier_business_key(corp)
    if not key:
        return "", "공급사 식별자 없음"
    identity, error = parse_category_history_identity(corp, item)
    if error:
        return "", error

    supplier = Supplier.objects.filter(business_no=key).first()
    is_duplicate = bool(
        supplier
        and CategoryContractHistory.objects.filter(
            supplier=supplier,
            source_api="나라장터",
            external_id=identity["external_id"],
        ).exists()
    )
    return ("category_duplicate" if is_duplicate else "category_new"), ""


def looks_like_address(value: str) -> bool:
    text = str(value or "").strip()
    return bool(
        text
        and re.search(r"\d", text)
        and any(token in text for token in ("시", "군", "구", "로", "길", "동", "읍", "면"))
    )


def extract_supplier_address(item: dict) -> str:
    for field in SUPPLIER_ADDRESS_FIELDS:
        value = str(item.get(field, "")).strip()
        if looks_like_address(value):
            return value
    return ""


def make_dry_run_sample(corp: dict, item: dict, matched_materials, status: str) -> str:
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
    institution = item.get("cntrctInsttNm", "미확인")
    return (
        f"{status} | {supplier_name} | {contract_name} | {material_labels} | "
        f"{match_basis} | {contract_date} | 계약기관(주소 아님): {institution}"
    )


def make_hold_sample(corp: dict, item: dict, reason: str) -> str:
    supplier_name = corp.get("name", "업체명 미확인")
    contract_name = (
        item.get("cntrctPrdctNm")
        or item.get("prdctIdntNoNm")
        or item.get("cntrctNm")
        or "계약명 미확인"
    )
    contract_date = item.get("cntrctCnclsDate", "날짜 미확인")
    return f"보류 | {supplier_name} | {contract_name} | {contract_date} | 사유: {reason}"


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

    if not name:
        return None

    key = supplier_business_key(corp)

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
    contract_date, unit_price, error = parse_history_identity(item)
    if error:
        print(f"    ⚠ 저장 제외: {error}")
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


def save_category_history(
    supplier: Supplier,
    material_category: str,
    search_keyword: str,
    mapping_reason: str,
    item: dict,
) -> tuple[bool, str]:
    identity, error = parse_category_history_identity(
        {"name": supplier.name, "business_no": supplier.business_no},
        item,
    )
    if error:
        return False, error

    try:
        raw_data = dict(item)
        raw_data["paceflowMappingStatus"] = "category_only"
        raw_data["paceflowMappingReason"] = mapping_reason
        raw_data["paceflowSearchKeyword"] = search_keyword
        raw_data["paceflowRelevanceBasis"] = item.get("_paceflow_relevance_basis", "")
        _, created = CategoryContractHistory.objects.get_or_create(
            supplier=supplier,
            source_api="나라장터",
            external_id=identity["external_id"],
            defaults={
                "material_category": material_category,
                "contract_date": identity["contract_date"],
                "contract_name": identity["contract_name"],
                "unit_price": identity["unit_price"],
                "quantity": identity["quantity"],
                "keyword": search_keyword,
                "mapping_status": "category_only",
                "mapping_reason": mapping_reason,
                "raw_data": raw_data,
            },
        )
        return created, ""
    except Exception as exc:
        return False, f"자재군 계약 저장 실패: {exc}"


# ──────────────────────────────────────────
# 6. 메인
# ──────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="나라장터 계약 이력 수집")
    parser.add_argument("--material", required=True, help="자재명 (예: 철근)")
    parser.add_argument("--search", help="검색어. 여러 개는 쉼표로 구분하며 생략하면 자재별 기본 검색어 사용")
    parser.add_argument("--year",     type=int, default=2025)
    parser.add_argument("--years", help="수집 연도. 여러 개는 쉼표로 구분 (예: 2024,2025,2026)")
    parser.add_argument("--start-date", help="조회 시작일 (YYYY-MM-DD, --year보다 우선)")
    parser.add_argument("--end-date", help="조회 종료일 (YYYY-MM-DD, --year보다 우선)")
    parser.add_argument("--start-page", type=int, default=1, help="조회 시작 페이지 (기본값: 1)")
    parser.add_argument("--pages",    type=int, default=5)
    parser.add_argument("--num-rows", type=int, default=10, help="페이지당 조회 건수 (기본값: 10)")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_SECONDS, help="API read timeout 초")
    parser.add_argument("--retries", type=int, default=DEFAULT_RETRIES, help="timeout 재시도 횟수")
    parser.add_argument("--retry-sleep", type=float, default=DEFAULT_RETRY_SLEEP_SECONDS, help="재시도 대기 초")
    parser.add_argument("--preview-limit", type=int, default=3, help="키워드별 대표 샘플 수")
    parser.add_argument("--dry-run", action="store_true", help="DB 저장 없이 매칭 결과만 확인")
    args = parser.parse_args()
    if args.start_page < 1:
        parser.error("--start-page는 1 이상이어야 합니다.")
    if args.pages < 1:
        parser.error("--pages는 1 이상이어야 합니다.")
    if args.num_rows < 1:
        parser.error("--num-rows는 1 이상이어야 합니다.")
    if args.timeout <= 0:
        parser.error("--timeout은 0보다 커야 합니다.")
    if args.retries < 0 or args.retry_sleep < 0 or args.preview_limit < 0:
        parser.error("--retries, --retry-sleep, --preview-limit은 0 이상이어야 합니다.")
    search_keywords = (
        [keyword.strip() for keyword in args.search.split(",") if keyword.strip()]
        if args.search
        else list(DEFAULT_SEARCH_KEYWORDS.get(args.material, (args.material,)))
    )
    if bool(args.start_date) != bool(args.end_date):
        parser.error("--start-date와 --end-date는 함께 지정해야 합니다.")

    periods = []
    if args.start_date and args.end_date:
        try:
            range_start = date.fromisoformat(args.start_date)
            range_end = date.fromisoformat(args.end_date)
        except ValueError:
            parser.error("날짜는 YYYY-MM-DD 형식이어야 합니다.")
        if range_start > range_end:
            parser.error("--start-date는 --end-date보다 늦을 수 없습니다.")
        range_days = (range_end - range_start).days + 1
        if range_days > 7:
            print(f"⚠ 조회기간 {range_days}일은 권장 최대 7일을 초과합니다.")
            if args.dry_run:
                print("dry-run 안전장치로 API 요청을 실행하지 않습니다.")
                return
        periods.append((range_start, range_end, f"{range_start}~{range_end}"))
        if args.years:
            print("안내: 날짜 범위가 지정되어 --years는 사용하지 않습니다.")
    else:
        try:
            years = (
                [int(year.strip()) for year in args.years.split(",") if year.strip()]
                if args.years
                else [args.year]
            )
        except ValueError:
            parser.error("--years는 2024,2025처럼 숫자와 쉼표로 입력하세요.")
        periods = [
            (date(year, 1, 1), date(year, 12, 31), f"{year}년")
            for year in years
        ]
        print("⚠ 연도 단위 조회는 API 지연 가능성이 큽니다. --start-date/--end-date로 7일 이내 조회를 권장합니다.")

    if not NARAJANGTEO_KEY:
        print("❌ NARAJANGTEO_API_KEY가 .env에 없습니다.")
        sys.exit(1)

    materials = Material.objects.filter(name__icontains=args.material)
    if not materials.exists():
        print(f"❌ '{args.material}' 자재가 DB에 없습니다. seed_data.py를 먼저 실행하세요.")
        sys.exit(1)
    material_category = MATERIAL_CATEGORY_CODES.get(args.material)
    if not material_category:
        print(f"❌ '{args.material}'에 대응하는 자재군 코드가 없습니다.")
        sys.exit(1)

    mode_label = "미리보기" if args.dry_run else "수집"
    end_page = args.start_page + args.pages - 1
    print(
        f"\n{mode_label} 시작: {args.material} / 검색어 {', '.join(search_keywords)} / "
        f"조회기간 {', '.join(label for _, _, label in periods)} / 페이지 {args.start_page}~{end_page} / "
        f"numRows={args.num_rows} / timeout={args.timeout:g}초 / retries={args.retries}회\n"
    )
    print("중복 기준: 자재=(KS 코드, KS 등급, 규격), 공급사=사업자번호/없으면 업체명 키, 계약=(공급사, 자재, 계약일, 계약금액)")
    print("자재군 계약 중복 기준: 공급사 + source_api + external_id (보류 계약은 SupplyHistory에 저장하지 않음)")
    if not JUSO_KEY:
        print("도로명주소 API 키 없음 (이번 계약 dry-run에는 영향 없음)")

    total_saved = 0
    total_category_saved = 0
    totals = Counter()
    failures = []

    for period_start, period_end, period_label in periods:
        for search_keyword in search_keywords:
            stats = Counter()
            exclusion_reasons = Counter()
            hold_reasons = Counter()
            samples = []
            hold_samples = []
            for page in range(args.start_page, args.start_page + args.pages):
                print(f"{period_label} / {search_keyword} / 페이지 {page} 수집 중...")
                try:
                    data = fetch_contracts(
                        search_keyword,
                        period_start,
                        period_end,
                        page,
                        num_rows=args.num_rows,
                        timeout_seconds=args.timeout,
                        retries=args.retries,
                        retry_sleep_seconds=args.retry_sleep,
                    )
                    fetch_meta = data.pop("_paceflow_fetch_meta", {})
                    response_meta = response_diagnostics(data, page, args.num_rows)
                    items = parse_contracts(data)
                    print(
                        f"  [health] HTTP={fetch_meta.get('status_code', '미확인')} "
                        f"응답시간={fetch_meta.get('elapsed_seconds', 0):.2f}초 "
                        f"totalCount={response_meta['total_count']} pageNo={response_meta['page_no']} "
                        f"numOfRows={response_meta['num_rows']} 후보={len(items)} "
                        f"code={response_meta['result_code']} message={response_meta['result_message']}"
                    )
                    print(
                        f"  [페이지 성공] API=나라장터 계약정보 키워드={search_keyword} 페이지={page} "
                        f"timeout={'예(재시도 후 복구)' if fetch_meta.get('recovered_after_timeout') else '아니오'} "
                        f"재시도={fetch_meta.get('retries_used', 0)}/{args.retries} 최종=성공"
                    )
                except PageFetchError as exc:
                    stats["failed_pages"] += 1
                    if exc.timed_out:
                        stats["timeout_pages"] += 1
                    failure = {
                        "api": "나라장터 계약정보",
                        "keyword": search_keyword,
                        "period": period_label,
                        "page": page,
                        "timeout": exc.timed_out,
                        "attempts": exc.attempts,
                        "status_code": exc.status_code,
                        "elapsed_seconds": exc.elapsed_seconds,
                        "message": str(exc),
                    }
                    failures.append(failure)
                    print(
                        f"  [페이지 실패] API=나라장터 계약정보 키워드={search_keyword} 페이지={page} "
                        f"기간={period_label} HTTP={exc.status_code or '없음'} "
                        f"응답시간={exc.elapsed_seconds or 0:.2f}초 "
                        f"timeout={'예' if exc.timed_out else '아니오'} 재시도={max(0, exc.attempts - 1)}/{args.retries} "
                        f"시도={exc.attempts} 최종=실패 ({exc})"
                    )
                    continue
                except ValueError as exc:
                    stats["failed_pages"] += 1
                    failures.append({
                        "api": "나라장터 계약정보",
                        "keyword": search_keyword,
                        "period": period_label,
                        "page": page,
                        "timeout": False,
                        "attempts": 1,
                        "status_code": fetch_meta.get("status_code"),
                        "elapsed_seconds": fetch_meta.get("elapsed_seconds"),
                        "message": f"응답 파싱 실패: {exc}",
                    })
                    print(
                        f"  [페이지 실패] API=나라장터 계약정보 키워드={search_keyword} 페이지={page} "
                        f"timeout=아니오 시도=1 최종=실패 (응답 파싱 실패: {exc})"
                    )
                    continue

                if not items:
                    print("  더 이상 데이터 없음. 다음 검색으로 이동.")
                    break
                stats["queried"] += len(items)

                for item in items:
                    is_relevant, relevance_reason = evaluate_material_relevance(item, args.material)
                    if not is_relevant:
                        stats["excluded"] += 1
                        exclusion_reasons[relevance_reason] += 1
                        continue

                    corp_list_str = item.get("corpList", "")
                    corps = parse_corp_list(corp_list_str)
                    if not corps:
                        stats["excluded"] += 1
                        exclusion_reasons["주계약업체 정보 없음"] += 1
                        continue

                    # 주계약업체만 저장
                    main_corp = corps[0]
                    matched_materials = choose_materials(materials, item, args.material)
                    if not matched_materials:
                        hold_reason = item.get("_paceflow_hold_reason")
                        if hold_reason:
                            stats["held"] += 1
                            hold_reasons[hold_reason] += 1
                            is_category_candidate = hold_reason in CATEGORY_HISTORY_HOLD_REASONS
                            category_status = ""
                            if is_category_candidate and args.dry_run:
                                category_status, category_error = classify_category_history_candidate(
                                    main_corp,
                                    material_category,
                                    item,
                                )
                                if category_error:
                                    stats["category_invalid"] += 1
                                    exclusion_reasons[f"자재군 계약 후보 적용 실패: {category_error}"] += 1
                                else:
                                    stats[category_status] += 1
                            elif is_category_candidate:
                                address = extract_supplier_address(item)
                                supplier = upsert_supplier(main_corp, address)
                                if not supplier:
                                    stats["category_invalid"] += 1
                                    exclusion_reasons["자재군 계약 공급사 upsert 실패"] += 1
                                else:
                                    created, category_error = save_category_history(
                                        supplier,
                                        material_category,
                                        search_keyword,
                                        hold_reason,
                                        item,
                                    )
                                    if category_error:
                                        stats["category_invalid"] += 1
                                        exclusion_reasons[category_error] += 1
                                    elif created:
                                        stats["category_saved"] += 1
                                        total_category_saved += 1
                                        print(
                                            f"  ✓ 자재군 이력 저장: {supplier.name} / {args.material} / "
                                            f"{item.get('cntrctCnclsDate')} / {hold_reason}"
                                        )
                                    else:
                                        stats["category_duplicate"] += 1
                            if len(hold_samples) < args.preview_limit:
                                sample = make_hold_sample(main_corp, item, hold_reason)
                                if is_category_candidate:
                                    label = {
                                        "category_new": "자재군 신규 후보",
                                        "category_duplicate": "자재군 기존 중복",
                                    }.get(category_status, "자재군 이력 대상")
                                    sample = f"{sample} | {label}"
                                else:
                                    sample = f"{sample} | 자재군 이력 저장 제외"
                                hold_samples.append(sample)
                        else:
                            stats["excluded"] += 1
                            exclusion_reasons["검색어와 품목 불일치"] += 1
                        continue

                    if args.dry_run:
                        classified, classification_error = classify_dry_run_candidates(
                            main_corp,
                            matched_materials,
                            item,
                        )
                        if classification_error:
                            stats["excluded"] += 1
                            exclusion_reasons[f"중복 기준 적용 실패: {classification_error}"] += 1
                            continue
                        for _, status in classified:
                            stats[status] += 1
                        if len(samples) < args.preview_limit:
                            statuses = {status for _, status in classified}
                            status_label = "중복" if statuses == {"duplicate"} else "신규"
                            samples.append(make_dry_run_sample(main_corp, item, matched_materials, status_label))
                        continue

                    address = extract_supplier_address(item)
                    supplier = upsert_supplier(main_corp, address)
                    if not supplier:
                        stats["excluded"] += 1
                        exclusion_reasons["공급사 upsert 실패"] += 1
                        continue

                    for material in matched_materials:
                        if save_history(supplier, material, item):
                            total_saved += 1
                            print(f"  ✓ 저장: {supplier.name} / {material} / {item.get('cntrctCnclsDate')}")

            totals.update(stats)
            print(
                f"  [키워드 요약] {period_label}/{search_keyword}: 조회 후보={stats['queried']}, "
                f"신규 후보={stats['new']}, 기존 중복={stats['duplicate']}, 보류={stats['held']}, "
                f"자재군 신규={stats['category_new']}, 자재군 중복={stats['category_duplicate']}, "
                f"자재군 저장={stats['category_saved']}, 제외={stats['excluded']}, "
                f"실패 페이지={stats['failed_pages']}, timeout 페이지={stats['timeout_pages']}"
            )
            if hold_reasons:
                print("  보류 사유: " + ", ".join(f"{reason} {count}건" for reason, count in hold_reasons.items()))
            if exclusion_reasons:
                print("  제외 사유: " + ", ".join(f"{reason} {count}건" for reason, count in exclusion_reasons.items()))
            if stats["duplicate"]:
                print(f"  중복 사유: 기존 DB 중복 {stats['duplicate']}건")
            if hold_samples:
                print("  보류 샘플:")
                for sample in hold_samples:
                    print(f"    - {sample}")
            if samples:
                print("  대표 샘플:")
                for sample in samples:
                    print(f"    - {sample}")

    if args.dry_run:
        print(
            f"\ndry-run 완료: 조회 후보={totals['queried']}, 신규 후보={totals['new']}, "
            f"기존 중복={totals['duplicate']}, 보류={totals['held']}, 제외={totals['excluded']}, "
            f"자재군 신규={totals['category_new']}, 자재군 중복={totals['category_duplicate']}, "
            f"실패 페이지={totals['failed_pages']}, timeout 페이지={totals['timeout_pages']} (DB 저장 없음)"
        )
        if failures:
            print("failed_requests:")
            for failure in failures:
                print(
                    f"  - API={failure['api']} 키워드={failure['keyword']} 기간={failure['period']} "
                    f"페이지={failure['page']} HTTP={failure.get('status_code') or '없음'} "
                    f"응답시간={failure.get('elapsed_seconds') or 0:.2f}초 "
                    f"timeout={'예' if failure['timeout'] else '아니오'} "
                    f"재시도={max(0, failure['attempts'] - 1)}/{args.retries} 시도={failure['attempts']} "
                    f"최종=실패 ({failure['message']})"
                )
            print("  가능성: API 서버 지연 / 조회기간 과다 / 검색 파라미터 문제 / 네트워크 경로 문제")
    else:
        print(
            f"\n✅ 완료: 정확 자재 이력 {total_saved}건 저장, "
            f"자재군 계약 이력 {total_category_saved}건 저장, 제외 {totals['excluded']}건"
        )


if __name__ == "__main__":
    main()
