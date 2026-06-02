"""
초기 데이터 적재 스크립트
실행: python manage.py shell < scripts/seed_data.py

KS D 3504:2022 (철근 콘크리트용 봉강) 기준값을 기반으로
Material, MaterialSpec, RegulationMapping을 생성한다.
"""

import os
import sys
import django

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from core.models import Material, MaterialSpec, RegulationMapping

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
print("다음 단계: python scripts/collect_narajangteo.py 실행")