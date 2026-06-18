"""
초기 데이터 적재 스크립트
실행: python manage.py shell < scripts/seed_data.py

KS D 3504:2022 (철근 콘크리트용 봉강) 기준값을 기반으로
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
# 출처: KS D 3504:2022 표 1
# ──────────────────────────────────────────

REBAR_DATA = [
    # (ks_grade, diameter, yield_min, yield_max, tensile_min, elongation_min, carbon_eq_max, astm, jis, requires_approval, approval_reason)
    ("SD300", "D10", 300, 420, 440, 16.0, 0.50, "A615 Gr40", "SD295A", False, ""),
    ("SD300", "D13", 300, 420, 440, 16.0, 0.50, "A615 Gr40", "SD295A", False, ""),
    ("SD300", "D16", 300, 420, 440, 16.0, 0.50, "A615 Gr40", "SD295A", False, ""),
    ("SD400", "D10", 400, 520, 560, 16.0, 0.50, "A615 Gr60", "SD390",  False, ""),
    ("SD400", "D13", 400, 520, 560, 16.0, 0.50, "A615 Gr60", "SD390",  False, ""),
    ("SD400", "D16", 400, 520, 560, 14.0, 0.50, "A615 Gr60", "SD390",  False, ""),
    ("SD400", "D19", 400, 520, 560, 14.0, 0.50, "A615 Gr60", "SD390",  False, ""),
    ("SD400", "D22", 400, 520, 560, 14.0, 0.50, "A615 Gr60", "SD390",  False, ""),
    ("SD500", "D10", 500, 650, 620, 12.0, 0.55, "A615 Gr75", "SD490",  True,  "SD500 이상은 항복강도 상향으로 구조 재계산 및 감리 승인이 필요합니다."),
    ("SD500", "D13", 500, 650, 620, 12.0, 0.55, "A615 Gr75", "SD490",  True,  "SD500 이상은 항복강도 상향으로 구조 재계산 및 감리 승인이 필요합니다."),
    ("SD500", "D16", 500, 650, 620, 12.0, 0.55, "A615 Gr75", "SD490",  True,  "SD500 이상은 항복강도 상향으로 구조 재계산 및 감리 승인이 필요합니다."),
    ("SD500", "D19", 500, 650, 620, 10.0, 0.55, "A615 Gr75", "SD490",  True,  "SD500 이상은 항복강도 상향으로 구조 재계산 및 감리 승인이 필요합니다."),
    ("SD600", "D13", 600, 780, 720, 10.0, 0.60, "A615 Gr87", "—",      True,  "SD600은 고강도 철근으로 구조 재계산 필수. 내진 구조 별도 검토 필요합니다."),
    ("SD600", "D16", 600, 780, 720, 10.0, 0.60, "A615 Gr87", "—",      True,  "SD600은 고강도 철근으로 구조 재계산 필수. 내진 구조 별도 검토 필요합니다."),
]

created_count = 0

for row in REBAR_DATA:
    (
        ks_grade, diameter,
        yield_min, yield_max, tensile_min, elongation_min, carbon_eq_max,
        astm, jis, requires_approval, approval_reason,
    ) = row

    is_seismic = ks_grade in ("SD400", "SD500")  # 내진 구조 적용 가능 등급

    material, created = Material.objects.get_or_create(
        ks_code="KS D 3504",
        ks_grade=ks_grade,
        diameter=diameter,
        defaults={
            "name":        "철근",
            "category":    "structural",
            "is_seismic":  is_seismic,
            "is_weldable": True,
        },
    )

    MaterialSpec.objects.get_or_create(
        material=material,
        defaults={
            "yield_strength_min":    yield_min,
            "yield_strength_max":    yield_max,
            "tensile_strength_min":  tensile_min,
            "elongation_min":        elongation_min,
            "carbon_equivalent_max": carbon_eq_max,
            "source":                "KS D 3504:2022",
        },
    )

    RegulationMapping.objects.get_or_create(
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

SUPPLY_HISTORY_DATA = [
    ("성수철강", candidate_material, 770000, 12000, 0),
    ("성수철강", candidate_material, 775000, 10000, 35),
    ("성수철강", candidate_material, 782000, 9000, 70),
    ("한강스틸", candidate_material, 755000, 8000, 5),
    ("한강스틸", candidate_material, 760000, 11000, 42),
    ("동부자재", candidate_material, 790000, 7000, 10),
    ("동부자재", candidate_material, 785000, 7500, 48),
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
