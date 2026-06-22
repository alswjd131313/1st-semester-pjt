"""
초기 데이터 적재 스크립트
실행: python manage.py shell < scripts/seed_data.py

KS D 3504:2025 (철근 콘크리트용 봉강), KS D 3503:2018 (일반 구조용 압연 강재),
KS D 3502:2022 (열간 압연 형강의 모양·치수·무게), KS L 5201:2021 (포틀랜드 시멘트)
기준값을 기반으로
Material, MaterialSpec, RegulationMapping을 생성한다.
"""

import os
import sys
import django
from datetime import date, timedelta

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from core.models import Material, MaterialSpec, RegulationMapping, Supplier, SupplyHistory

# ──────────────────────────────────────────
# 철근 (KS D 3504) 시드 데이터
# 출처: KS D 3504:2025 표 1(종류), 표 2(화학 성분), 표 3(기계적 성질)
# 현재 모델은 탄소당량 중심으로 화학 성분을 저장한다.
# ──────────────────────────────────────────

REBAR_DIAMETERS = ("D10", "D13", "D16", "D19", "D22")

APPROVAL_REASONS = {
    "high_strength": "SD500 이상 고강도 철근은 구조 재검토 및 감리 승인 확인이 필요합니다.",
    "weldable": "용접용 철근은 용접 시공 조건과 품질검사 기준 확인이 필요합니다.",
    "seismic": "특수내진용 철근은 내진 설계 적용 여부와 감리 승인 확인이 필요합니다.",
}

REBAR_DATA = [
    # (ks_grade, yield_min, yield_max, tensile_min, elongation_min, carbon_eq_max, astm, jis, requires_approval, approval_reason, is_seismic, is_weldable)
    ("SD300",   300, 420, 440, 16.0, None, "A615 Gr40", "SD295A", False, "", False, False),
    ("SD400",   400, 520, 560, 16.0, None, "A615 Gr60", "SD390",  False, "", True,  False),
    ("SD500",   500, 650, 620, 12.0, None, "A615 Gr75", "SD490",  True,  APPROVAL_REASONS["high_strength"], True,  False),
    ("SD600",   600, 780, 720, 10.0, 0.67, "A615 Gr80", "",       True,  APPROVAL_REASONS["high_strength"], True,  False),
    ("SD700",   700, 910, 756, 10.0, 0.67, "",          "",       True,  APPROVAL_REASONS["high_strength"], True,  False),
    ("SD400 W", 400, 520, 560, 16.0, 0.50, "A706 Gr60", "",       True,  APPROVAL_REASONS["weldable"],      False, True),
    ("SD500 W", 500, 650, 620, 12.0, 0.50, "A706 Gr80", "",       True,  f"{APPROVAL_REASONS['weldable']} {APPROVAL_REASONS['high_strength']}", False, True),
    ("SD400 S", 400, 520, 560, 16.0, 0.55, "",          "",       True,  APPROVAL_REASONS["seismic"],       True,  False),
    ("SD500 S", 500, 620, 625, 12.0, 0.60, "",          "",       True,  f"{APPROVAL_REASONS['seismic']} {APPROVAL_REASONS['high_strength']}", True, False),
    ("SD600 S", 600, 720, 750, 10.0, 0.70, "",          "",       True,  f"{APPROVAL_REASONS['seismic']} {APPROVAL_REASONS['high_strength']}", True, False),
    ("SD700 S", 700, 820, 875, 10.0, 0.80, "",          "",       True,  f"{APPROVAL_REASONS['seismic']} {APPROVAL_REASONS['high_strength']}", True, False),
]

created_count = 0

for row in REBAR_DATA:
    (
        ks_grade,
        yield_min, yield_max, tensile_min, elongation_min, carbon_eq_max,
        astm, jis, requires_approval, approval_reason, is_seismic, is_weldable,
    ) = row

    for diameter in REBAR_DIAMETERS:
        material, created = Material.objects.update_or_create(
            ks_code="KS D 3504",
            ks_grade=ks_grade,
            diameter=diameter,
            defaults={
                "name":        "철근",
                "category":    "structural",
                "material_group": "rebar",
                "material_subtype": "deformed_rebar",
                "is_seismic":  is_seismic,
                "is_weldable": is_weldable,
            },
        )

        MaterialSpec.objects.update_or_create(
            material=material,
            defaults={
                "yield_strength_min":    yield_min,
                "yield_strength_max":    yield_max,
                "tensile_strength_min":  tensile_min,
                "elongation_min":        elongation_min,
                "carbon_equivalent_max": carbon_eq_max,
                "source":                "KS D 3504:2025 표 2·표 3",
            },
        )

        RegulationMapping.objects.update_or_create(
            material=material,
            defaults={
                "astm_code":         astm,
                "jis_code":          jis,
                "requires_approval": requires_approval,
                "approval_reason":   approval_reason,
            },
        )

        if created:
            created_count += 1
            print(f"  ✓ 생성: 철근 {ks_grade} {diameter}")

print(f"\n완료: {created_count}개 자재 레코드 생성됨")

# ──────────────────────────────────────────
# H빔/형강 시드 데이터
# 재질/강도 출처: KS D 3503:2018 표 1(종류), 표 2(화학 성분), 표 3(기계적 성질)
# 치수 출처: KS D 3502:2022 표 1(형강 종류), 부표 9(H형강 표준 단면치수)
# 현재 모델은 대표 형강 두께 구간의 보수적 최솟값과 표준 호칭 치수를 저장한다.
# ──────────────────────────────────────────

STRUCTURAL_STEEL_SIZES = (
    "H-100x100",
    "H-150x75",
    "H-150x150",
    "H-200x100",
    "H-200x200",
    "H-250x125",
    "H-250x250",
    "H-300x150",
    "H-300x300",
    "H-350x175",
    "H-350x350",
    "H-400x200",
    "H-400x400",
    "H-600x200",
    "H-700x300",
)

STRUCTURAL_STEEL_DATA = [
    # (ks_grade, yield_min, yield_max, tensile_min, elongation_min, approval_required, approval_reason)
    ("SS235", 195, None, 330, 21.0, False, ""),
    ("SS275", 235, None, 410, 18.0, False, ""),
    ("SS315", 275, None, 490, 16.0, False, ""),
    ("SS410", 400, None, 540, 14.0, True, "SS410 이상 고강도 구조용 강재는 구조 검토와 사용 부위 확인이 필요합니다."),
    ("SS450", 440, None, 590, 10.0, True, "SS450 이상 고강도 구조용 강재는 구조 검토와 사용 부위 확인이 필요합니다."),
    ("SS550", 540, None, 690, 11.0, True, "SS550 고강도 구조용 강재는 구조 검토와 감리 승인 확인이 필요합니다."),
]

structural_created_count = 0

for row in STRUCTURAL_STEEL_DATA:
    (
        ks_grade,
        yield_min, yield_max, tensile_min, elongation_min,
        requires_approval, approval_reason,
    ) = row

    for size in STRUCTURAL_STEEL_SIZES:
        material, created = Material.objects.update_or_create(
            ks_code="KS D 3503",
            ks_grade=ks_grade,
            diameter=size,
            defaults={
                "name":        "H빔",
                "category":    "structural",
                "material_group": "shape_steel",
                "material_subtype": "h_beam",
                "is_seismic":  False,
                "is_weldable": False,
            },
        )

        MaterialSpec.objects.update_or_create(
            material=material,
            defaults={
                "yield_strength_min":    yield_min,
                "yield_strength_max":    yield_max,
                "tensile_strength_min":  tensile_min,
                "elongation_min":        elongation_min,
                "carbon_equivalent_max": None,
                "source":                "KS D 3503:2018 표 3 / KS D 3502:2022 부표 9",
            },
        )

        RegulationMapping.objects.update_or_create(
            material=material,
            defaults={
                "astm_code":         "",
                "jis_code":          "",
                "requires_approval": requires_approval,
                "approval_reason":   approval_reason,
            },
        )

        if created:
            structural_created_count += 1
            print(f"  ✓ 생성: H빔 {ks_grade} {size}")

print(f"완료: {structural_created_count}개 H빔/압연강재 레코드 생성됨")

# ──────────────────────────────────────────
# 시멘트 시드 데이터
# 출처: KS L 5201:2021 표 1(화학 성분), 표 2(물리 성능)
# 현재 MaterialSpec 모델은 철강 물성 필드 중심이므로,
# yield_strength_min에는 조기 압축강도, tensile_strength_min에는 28일 압축강도,
# carbon_equivalent_max에는 SO3 상한을 임시 매핑한다.
# ──────────────────────────────────────────

CEMENT_DATA = [
    # (ks_grade, early_strength_label, early_strength_min, strength_28d_min, so3_max, source_note)
    ("1종", "3일", 12.5, 42.5, 3.5, "보통 포틀랜드 시멘트"),
    ("2종", "3일", 7.5, 32.5, 3.0, "중용열 포틀랜드 시멘트"),
    ("3종", "1일", 10.0, 47.5, 4.5, "조강 포틀랜드 시멘트"),
    ("4종", "7일", 7.5, 22.5, 3.5, "저열 포틀랜드 시멘트"),
    ("5종", "3일", 10.0, 40.0, 3.0, "내황산염 포틀랜드 시멘트"),
]

cement_created_count = 0

for ks_grade, early_label, early_strength, strength_28d, so3_max, source_note in CEMENT_DATA:
    material, created = Material.objects.update_or_create(
        ks_code="KS L 5201",
        ks_grade=ks_grade,
        diameter="40kg 포대",
        defaults={
            "name":        "시멘트",
            "category":    "non_structural",
            "material_group": "cement",
            "material_subtype": (
                "ordinary_portland" if ks_grade == "1종"
                else "high_early_strength" if ks_grade == "3종"
                else "other"
            ),
            "is_seismic":  False,
            "is_weldable": False,
        },
    )

    MaterialSpec.objects.update_or_create(
        material=material,
        defaults={
            "yield_strength_min":    early_strength,
            "yield_strength_max":    None,
            "tensile_strength_min":  strength_28d,
            "elongation_min":        0,
            "carbon_equivalent_max": so3_max,
            "source":                f"KS L 5201:2021 표 1·표 2 ({source_note}, 조기강도 {early_label})",
        },
    )

    RegulationMapping.objects.update_or_create(
        material=material,
        defaults={
            "astm_code":         "",
            "jis_code":          "",
            "requires_approval": ks_grade in ("2종", "3종", "4종", "5종"),
            "approval_reason":   "" if ks_grade == "1종" else f"{source_note}는 용도와 양생 조건에 따라 현장 품질 기준 확인이 필요합니다.",
        },
    )

    if created:
        cement_created_count += 1
        print(f"  ✓ 생성: 시멘트 {ks_grade} 40kg 포대")

print(f"완료: {cement_created_count}개 포틀랜드 시멘트 레코드 생성됨")

# ──────────────────────────────────────────
# KS 단열재 물성 기준 수동 DB
# MaterialSpec 필드 매핑:
# - yield_strength_min: 압축강도 또는 밀도 기준(kPa/kg/m3)
# - tensile_strength_min: 열성능 지수(낮은 열전도율 또는 높은 열저항일수록 높음)
# - carbon_equivalent_max: 흡수성/투습도 등 수분 관련 상한 기준
# ──────────────────────────────────────────

def thermal_score_from_mw(mw):
    return round(1000 / mw, 2)

INSULATION_DATA = [
    {
        "ks_code": "KS M 3880",
        "grade": "셀룰로오스 폼 1호",
        "size": "50T",
        "compression": 30,
        "thermal_score": thermal_score_from_mw(34),
        "moisture_limit": 4.0,
        "source": "KS M 3880:2011 표 1 - 밀도 30kg/m3 이상, 열전도도 0.034W/(m·K) 이하, 흡수성 4% 이하",
        "approval_reason": "셀룰로오스 폼 단열재는 밀도, 열전도도, 흡수성, 유해성 기준 확인이 필요합니다.",
    },
    {
        "ks_code": "KS M 3880",
        "grade": "셀룰로오스 폼 2호",
        "size": "50T",
        "compression": 25,
        "thermal_score": thermal_score_from_mw(35),
        "moisture_limit": 4.0,
        "source": "KS M 3880:2011 표 1 - 밀도 25kg/m3 이상, 열전도도 0.035W/(m·K) 이하, 흡수성 4% 이하",
        "approval_reason": "셀룰로오스 폼 단열재는 밀도, 열전도도, 흡수성, 유해성 기준 확인이 필요합니다.",
    },
    {
        "ks_code": "KS M 3880",
        "grade": "셀룰로오스 폼 3호",
        "size": "50T",
        "compression": 20,
        "thermal_score": thermal_score_from_mw(37),
        "moisture_limit": 4.0,
        "source": "KS M 3880:2011 표 1 - 밀도 20kg/m3 이상, 열전도도 0.037W/(m·K) 이하, 흡수성 4% 이하",
        "approval_reason": "셀룰로오스 폼 단열재는 밀도, 열전도도, 흡수성, 유해성 기준 확인이 필요합니다.",
    },
    {
        "ks_code": "KS M 3871-1",
        "grade": "분무식 PUR 1종 A",
        "size": "50T",
        "compression": 100,
        "thermal_score": 38.4,
        "moisture_limit": 4.5,
        "source": "KS M 3871-1:2025 표 1 - 압축강도 100kPa 이상, LTTR 1.92m2·K/W 이상, 수증기 투과도 4.5 이하",
        "approval_reason": "분무식 폴리우레탄 폼 단열재는 압축강도, 장기 열저항, 수증기 투과도 기준 확인이 필요합니다.",
    },
    {
        "ks_code": "KS M 3871-1",
        "grade": "분무식 PUR 1종 B",
        "size": "50T",
        "compression": 80,
        "thermal_score": 29.4,
        "moisture_limit": 9.0,
        "source": "KS M 3871-1:2025 표 1 - 압축강도 80kPa 이상, LTTR 1.47m2·K/W 이상, 수증기 투과도 9.0 이하",
        "approval_reason": "분무식 폴리우레탄 폼 단열재는 압축강도, 장기 열저항, 수증기 투과도 기준 확인이 필요합니다.",
    },
    {
        "ks_code": "KS M 3871-1",
        "grade": "분무식 PUR 2종 A",
        "size": "50T",
        "compression": 170,
        "thermal_score": 38.4,
        "moisture_limit": 4.5,
        "source": "KS M 3871-1:2025 표 1 - 압축강도 170kPa 이상, LTTR 1.92m2·K/W 이상, 수증기 투과도 4.5 이하",
        "approval_reason": "분무식 폴리우레탄 폼 단열재는 압축강도, 장기 열저항, 수증기 투과도 기준 확인이 필요합니다.",
    },
    {
        "ks_code": "KS M 3871-1",
        "grade": "분무식 PUR 2종 B",
        "size": "50T",
        "compression": 170,
        "thermal_score": 29.4,
        "moisture_limit": 4.5,
        "source": "KS M 3871-1:2025 표 1 - 압축강도 170kPa 이상, LTTR 1.47m2·K/W 이상, 수증기 투과도 4.5 이하",
        "approval_reason": "분무식 폴리우레탄 폼 단열재는 압축강도, 장기 열저항, 수증기 투과도 기준 확인이 필요합니다.",
    },
    {
        "ks_code": "KS M ISO 4898",
        "grade": "EPS II A-1",
        "size": "50T",
        "compression": 100,
        "thermal_score": thermal_score_from_mw(32),
        "moisture_limit": 4.0,
        "source": "KS M ISO 4898:2018 표 3 - EPS II A-1, 압축강도 100kPa 이상, 초기 열전도도 32mW/(m·K) 이하",
        "approval_reason": "EPS 단열재는 압축강도, 열전도도, 흡수성, 난연성 기준 확인이 필요합니다.",
    },
    {
        "ks_code": "KS M ISO 4898",
        "grade": "EPS III A-1",
        "size": "50T",
        "compression": 150,
        "thermal_score": thermal_score_from_mw(29),
        "moisture_limit": 2.0,
        "source": "KS M ISO 4898:2018 표 3 - EPS III A-1, 압축강도 150kPa 이상, 초기 열전도도 29mW/(m·K) 이하",
        "approval_reason": "EPS 단열재는 압축강도, 열전도도, 흡수성, 난연성 기준 확인이 필요합니다.",
    },
    {
        "ks_code": "KS M ISO 4898",
        "grade": "XPS II B-1",
        "size": "50T",
        "compression": 250,
        "thermal_score": thermal_score_from_mw(26),
        "moisture_limit": 1.0,
        "source": "KS M ISO 4898:2018 표 4 - XPS II B-1, 압축강도 250kPa 이상, 초기 열전도도 26mW/(m·K) 이하",
        "approval_reason": "XPS 단열재는 압축강도, 열전도도, 흡수성, 치수 안정성 기준 확인이 필요합니다.",
    },
    {
        "ks_code": "KS M ISO 4898",
        "grade": "XPS III B-2",
        "size": "50T",
        "compression": 450,
        "thermal_score": thermal_score_from_mw(26),
        "moisture_limit": 1.0,
        "source": "KS M ISO 4898:2018 표 4 - XPS III B-2, 압축강도 450kPa 이상, 초기 열전도도 26mW/(m·K) 이하",
        "approval_reason": "XPS 단열재는 압축강도, 열전도도, 흡수성, 치수 안정성 기준 확인이 필요합니다.",
    },
    {
        "ks_code": "KS M ISO 4898",
        "grade": "PUR II A",
        "size": "50T",
        "compression": 100,
        "thermal_score": thermal_score_from_mw(23),
        "moisture_limit": 3.0,
        "source": "KS M ISO 4898:2018 표 5 - PUR II A, 압축강도 100kPa 이상, 초기 열전도도 23mW/(m·K) 이하",
        "approval_reason": "PUR 단열재는 압축강도, 열전도도, 흡수성, 유해가스 기준 확인이 필요합니다.",
    },
    {
        "ks_code": "KS M ISO 4898",
        "grade": "PUR III A",
        "size": "50T",
        "compression": 150,
        "thermal_score": thermal_score_from_mw(23),
        "moisture_limit": 3.0,
        "source": "KS M ISO 4898:2018 표 5 - PUR III A, 압축강도 150kPa 이상, 초기 열전도도 23mW/(m·K) 이하",
        "approval_reason": "PUR 단열재는 압축강도, 열전도도, 흡수성, 유해가스 기준 확인이 필요합니다.",
    },
    {
        "ks_code": "KS M ISO 4898",
        "grade": "PF II A",
        "size": "50T",
        "compression": 100,
        "thermal_score": thermal_score_from_mw(22),
        "moisture_limit": 4.0,
        "source": "KS M ISO 4898:2018 표 6 - PF II A, 압축강도 100kPa 이상, 초기 열전도도 22mW/(m·K) 이하",
        "approval_reason": "PF 단열재는 압축강도, 열전도도, 흡수성, 난연성 기준 확인이 필요합니다.",
    },
    {
        "ks_code": "KS M ISO 4898",
        "grade": "PF III A",
        "size": "50T",
        "compression": 250,
        "thermal_score": thermal_score_from_mw(39),
        "moisture_limit": 4.0,
        "source": "KS M ISO 4898:2018 표 6 - PF III A, 압축강도 250kPa 이상, 초기 열전도도 39mW/(m·K) 이하",
        "approval_reason": "PF 단열재는 압축강도, 열전도도, 흡수성, 난연성 기준 확인이 필요합니다.",
    },
]

insulation_created_count = 0
for item in INSULATION_DATA:
    material, created = Material.objects.update_or_create(
        ks_code=item["ks_code"],
        ks_grade=item["grade"],
        diameter=item["size"],
        defaults={
            "name": "단열재",
            "category": "non_structural",
            "material_group": "insulation",
            "material_subtype": (
                "eps" if "EPS" in item["grade"]
                else "xps" if "XPS" in item["grade"]
                else "rigid_polyurethane" if "PUR" in item["grade"]
                else "glass_wool" if "글라스울" in item["grade"]
                else "other"
            ),
            "is_seismic": False,
            "is_weldable": False,
        },
    )
    MaterialSpec.objects.update_or_create(
        material=material,
        defaults={
            "yield_strength_min": item["compression"],
            "yield_strength_max": None,
            "tensile_strength_min": item["thermal_score"],
            "elongation_min": 0,
            "carbon_equivalent_max": item["moisture_limit"],
            "source": item["source"],
        },
    )
    RegulationMapping.objects.update_or_create(
        material=material,
        defaults={
            "astm_code": "",
            "jis_code": "",
            "requires_approval": False,
            "approval_reason": item["approval_reason"],
        },
    )
    if created:
        insulation_created_count += 1

print(f"완료: {insulation_created_count}개 단열재 레코드 생성됨")

# ──────────────────────────────────────────
# 전선관 시드 데이터
# 출처: KS C IEC 61386-1 일반 요구사항
# MaterialSpec 필드 매핑:
# - yield_strength_min: 압축 분류 하한(N)
# - tensile_strength_min: 충격 분류 등급
# - carbon_equivalent_max: 굽힘/시공 조건 점검 플래그(0=현장 확인)
# ──────────────────────────────────────────

CONDUIT_DATA = [
    ("16C", "경질 합성수지관", "rigid_conduit", 750, 2, "KS C IEC 61386-1 일반 요구사항 - 압축/충격/굽힘 특성 확인"),
    ("22C", "경질 합성수지관", "rigid_conduit", 750, 2, "KS C IEC 61386-1 일반 요구사항 - 압축/충격/굽힘 특성 확인"),
    ("28C", "경질 합성수지관", "rigid_conduit", 750, 2, "KS C IEC 61386-1 일반 요구사항 - 압축/충격/굽힘 특성 확인"),
    ("36C", "경질 합성수지관", "rigid_conduit", 750, 2, "KS C IEC 61386-1 일반 요구사항 - 압축/충격/굽힘 특성 확인"),
    ("16F", "가요 전선관", "flexible_conduit", 320, 2, "KS C IEC 61386-1 일반 요구사항 - 압축/충격/굽힘 특성 확인"),
    ("22F", "가요 전선관", "flexible_conduit", 320, 2, "KS C IEC 61386-1 일반 요구사항 - 압축/충격/굽힘 특성 확인"),
    ("16CD", "CD관", "cd_conduit", 320, 2, "KS C IEC 61386-1 일반 요구사항 - 압축/충격/온도 특성 확인"),
    ("22CD", "CD관", "cd_conduit", 320, 2, "KS C IEC 61386-1 일반 요구사항 - 압축/충격/온도 특성 확인"),
    ("16PF", "PF관", "pf_conduit", 750, 2, "KS C IEC 61386-1 일반 요구사항 - 압축/충격/온도 특성 확인"),
    ("22PF", "PF관", "pf_conduit", 750, 2, "KS C IEC 61386-1 일반 요구사항 - 압축/충격/온도 특성 확인"),
]

conduit_created_count = 0
for size, ks_grade, material_subtype, compression_class, impact_class, source_note in CONDUIT_DATA:
    material, created = Material.objects.update_or_create(
        ks_code="KS C IEC 61386-1",
        ks_grade=ks_grade,
        diameter=size,
        defaults={
            "name": "전선관",
            "category": "non_structural",
            "material_group": "electrical_conduit",
            "material_subtype": material_subtype,
            "is_seismic": False,
            "is_weldable": False,
        },
    )
    MaterialSpec.objects.update_or_create(
        material=material,
        defaults={
            "yield_strength_min": compression_class,
            "yield_strength_max": None,
            "tensile_strength_min": impact_class,
            "elongation_min": 0,
            "carbon_equivalent_max": 0,
            "source": source_note,
        },
    )
    RegulationMapping.objects.update_or_create(
        material=material,
        defaults={
            "astm_code": "",
            "jis_code": "",
            "requires_approval": False,
            "approval_reason": "전선관 타입별 세부 요구사항은 현장 적용 조건에 따라 검토 필요합니다.",
        },
    )
    if created:
        conduit_created_count += 1

print(f"완료: {conduit_created_count}개 전선관 레코드 생성됨")


# ──────────────────────────────────────────
# MVP 추천 API 확인용 공급사/납품 이력
# ──────────────────────────────────────────

SUPPLIER_DATA = [
    {
        "name": "성수철강",
        "business_no": "PF-1001",
        "address": "서울특별시 성동구 아차산로 123",
        "latitude": 37.544700,
        "longitude": 127.055800,
        "phone": "02-1234-5678",
    },
    {
        "name": "한강스틸",
        "business_no": "PF-1002",
        "address": "서울특별시 광진구 동일로 210",
        "latitude": 37.548300,
        "longitude": 127.072900,
        "phone": "02-2345-6789",
    },
    {
        "name": "동부자재",
        "business_no": "PF-1003",
        "address": "서울특별시 송파구 올림픽로 300",
        "latitude": 37.514500,
        "longitude": 127.103000,
        "phone": "02-3456-7890",
    },
    {
        "name": "수도권시멘트",
        "business_no": "PF-2001",
        "address": "서울특별시 강동구 천호대로 1100",
        "latitude": 37.535800,
        "longitude": 127.132500,
        "phone": "02-4567-8801",
    },
    {
        "name": "동서울건재",
        "business_no": "PF-2002",
        "address": "경기도 하남시 미사대로 510",
        "latitude": 37.567500,
        "longitude": 127.190400,
        "phone": "031-456-8802",
    },
    {
        "name": "한강레미콘",
        "business_no": "PF-2003",
        "address": "서울특별시 광진구 강변북로 220",
        "latitude": 37.536900,
        "longitude": 127.085700,
        "phone": "02-4567-8803",
    },
    {
        "name": "서울단열자재",
        "business_no": "PF-3001",
        "address": "서울특별시 성동구 광나루로 180",
        "latitude": 37.548900,
        "longitude": 127.059300,
        "phone": "02-555-3001",
    },
    {
        "name": "경기건축단열",
        "business_no": "PF-3002",
        "address": "경기도 구리시 벌말로 145",
        "latitude": 37.594100,
        "longitude": 127.132700,
        "phone": "031-555-3002",
    },
    {
        "name": "그린폼시스템",
        "business_no": "PF-3003",
        "address": "경기도 남양주시 다산중앙로 82",
        "latitude": 37.625900,
        "longitude": 127.153200,
        "phone": "031-555-3003",
    },
]

supplier_map = {}
for supplier_data in SUPPLIER_DATA:
    supplier, _ = Supplier.objects.update_or_create(
        business_no=supplier_data["business_no"],
        defaults={**supplier_data, "source": "manual"},
    )
    supplier_map[supplier_data["name"]] = supplier

candidate_material = Material.objects.get(
    ks_code="KS D 3504",
    ks_grade="SD400",
    diameter="D13",
)

h_beam_candidate_material = Material.objects.get(
    ks_code="KS D 3503",
    ks_grade="SS275",
    diameter="H-300x300",
)

cement_candidate_material = Material.objects.get(
    ks_code="KS L 5201",
    ks_grade="1종",
    diameter="40kg 포대",
)

insulation_candidate_material = Material.objects.get(
    ks_code="KS M ISO 4898",
    ks_grade="XPS II B-1",
    diameter="50T",
)

SUPPLY_HISTORY_DATA = [
    ("성수철강", candidate_material, 770000, 12000, 0),
    ("성수철강", candidate_material, 775000, 10000, 35),
    ("성수철강", candidate_material, 782000, 9000, 70),
    ("한강스틸", candidate_material, 755000, 8000, 5),
    ("한강스틸", candidate_material, 760000, 11000, 42),
    ("동부자재", candidate_material, 790000, 7000, 10),
    ("동부자재", candidate_material, 785000, 7500, 48),
    ("성수철강", h_beam_candidate_material, 1280000, 20, 12),
    ("한강스틸", h_beam_candidate_material, 1265000, 18, 30),
    ("동부자재", h_beam_candidate_material, 1310000, 16, 55),
    ("수도권시멘트", cement_candidate_material, 98000, 3000, 8),
    ("수도권시멘트", cement_candidate_material, 101000, 2800, 40),
    ("동서울건재", cement_candidate_material, 96000, 2400, 15),
    ("동서울건재", cement_candidate_material, 99000, 2600, 58),
    ("한강레미콘", cement_candidate_material, 103000, 3200, 22),
    ("한강레미콘", cement_candidate_material, 100000, 3000, 62),
    ("서울단열자재", insulation_candidate_material, 18200, 500, 6),
    ("서울단열자재", insulation_candidate_material, 18800, 450, 39),
    ("경기건축단열", insulation_candidate_material, 17500, 600, 14),
    ("경기건축단열", insulation_candidate_material, 17900, 550, 57),
    ("그린폼시스템", insulation_candidate_material, 19400, 420, 21),
    ("그린폼시스템", insulation_candidate_material, 19000, 470, 63),
]

for supplier_name, material, unit_price, quantity, days_ago in SUPPLY_HISTORY_DATA:
    SupplyHistory.objects.update_or_create(
        supplier=supplier_map[supplier_name],
        material=material,
        contract_date=date.today() - timedelta(days=days_ago),
        defaults={
            "unit_price": unit_price,
            "quantity": quantity,
            "raw_data": {"source": "PaceFlow MVP seed"},
        },
    )

print("완료: MVP 추천 확인용 공급사 3곳과 납품 이력을 적재했습니다.")
print("다음 단계: 실제 데이터가 필요하면 python scripts/collect_narajangteo.py 실행")
