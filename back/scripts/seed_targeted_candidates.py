"""H빔·전선관 추천 랭킹용 MVP 시드 후보를 적재한다.

실행: python scripts/seed_targeted_candidates.py
실데이터와 혼동되지 않도록 공급사와 이력 출처를 PaceFlow MVP seed로 저장한다.
"""

import os
import sys
from datetime import date

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from core.models import Material, Supplier, SupplyHistory


H_BEAM_CANDIDATES = (
    {
        "supplier": ("서서울형강", "PF-MVP-H001", "서울특별시 영등포구 경인로 775", 37.514200, 126.907500),
        "spec": ("SS275", "H-300x300"),
        "prices": (1275000, 1268000, 1260000),
    },
    {
        "supplier": ("경기남부철강", "PF-MVP-H002", "경기도 성남시 중원구 둔촌대로 388", 37.432600, 127.167900),
        "spec": ("SS275", "H-200x200"),
        "prices": (1240000, 1235000, 1228000),
    },
    {
        "supplier": ("인천형강센터", "PF-MVP-H003", "인천광역시 서구 봉수대로 141", 37.508400, 126.676100),
        "spec": ("SS315", "H-300x300"),
        "prices": (1345000, 1338000, 1330000),
    },
    {
        "supplier": ("남양주구조강재", "PF-MVP-H004", "경기도 남양주시 진건읍 진관산단로 68", 37.654200, 127.181700),
        "spec": ("SS275", "H-350x350"),
        "prices": (1295000, 1287000, 1280000),
    },
    {
        "supplier": ("하남형강물류", "PF-MVP-H005", "경기도 하남시 초광산단로 95", 37.540400, 127.164500),
        "spec": ("SS235", "H-250x250"),
        "prices": (1215000, 1208000, 1200000),
    },
    {
        "supplier": ("김포스틸센터", "PF-MVP-H006", "경기도 김포시 양촌읍 황금로 117", 37.619300, 126.626800),
        "spec": ("SS275", "H-400x200"),
        "prices": (1305000, 1298000, 1290000),
    },
)

CONDUIT_CANDIDATES = (
    {
        "supplier": ("서울전기배관", "PF-MVP-C001", "서울특별시 구로구 경인로53길 15", 37.503900, 126.879700),
        "spec": ("경질 합성수지관", "16C"),
        "prices": (2450, 2390, 2350),
    },
    {
        "supplier": ("동서울전재", "PF-MVP-C002", "서울특별시 광진구 동일로 350", 37.566800, 127.075700),
        "spec": ("경질 합성수지관", "22C"),
        "prices": (3150, 3080, 3020),
    },
    {
        "supplier": ("경기전선관유통", "PF-MVP-C003", "경기도 구리시 동구릉로 200", 37.614600, 127.139900),
        "spec": ("경질 합성수지관", "28C"),
        "prices": (4100, 4020, 3950),
    },
    {
        "supplier": ("인천전기자재", "PF-MVP-C004", "인천광역시 부평구 평천로 141", 37.519400, 126.713900),
        "spec": ("경질 합성수지관", "36C"),
        "prices": (5650, 5520, 5400),
    },
    {
        "supplier": ("하남배관자재", "PF-MVP-C005", "경기도 하남시 조정대로 150", 37.545100, 127.189000),
        "spec": ("가요 전선관", "16F"),
        "prices": (2850, 2790, 2730),
    },
    {
        "supplier": ("남양주전설자재", "PF-MVP-C006", "경기도 남양주시 다산중앙로 82", 37.625900, 127.153200),
        "spec": ("가요 전선관", "22F"),
        "prices": (3750, 3680, 3600),
    },
    {
        "supplier": ("성남전기유통", "PF-MVP-C007", "경기도 성남시 수정구 산성대로 305", 37.445200, 127.147100),
        "spec": ("경질 합성수지관", "22C"),
        "prices": (3200, 3130, 3060),
    },
    {
        "supplier": ("고양전선관물류", "PF-MVP-C008", "경기도 고양시 덕양구 통일로 140", 37.647300, 126.883500),
        "spec": ("경질 합성수지관", "28C"),
        "prices": (4180, 4090, 4000),
    },
)

CONTRACT_DATES = (date(2026, 3, 15), date(2026, 4, 15), date(2026, 5, 15))


def seed_candidates(category: str, ks_code: str, candidates: tuple[dict, ...]) -> int:
    saved = 0
    for candidate in candidates:
        name, business_no, address, latitude, longitude = candidate["supplier"]
        grade, diameter = candidate["spec"]
        supplier, _ = Supplier.objects.update_or_create(
            business_no=business_no,
            defaults={
                "name": name,
                "address": address,
                "latitude": latitude,
                "longitude": longitude,
                "source": "manual",
            },
        )
        material = Material.objects.get(
            name=category,
            ks_code=ks_code,
            ks_grade=grade,
            diameter=diameter,
        )

        for contract_date, unit_price in zip(CONTRACT_DATES, candidate["prices"]):
            _, created = SupplyHistory.objects.update_or_create(
                supplier=supplier,
                material=material,
                contract_date=contract_date,
                defaults={
                    "unit_price": unit_price,
                    "quantity": 20 if category == "H빔" else 1000,
                    "raw_data": {
                        "source": "PaceFlow MVP seed",
                        "contractName": f"{category} {grade} {diameter} 납품 이력 샘플",
                        "paceflowMatchBasis": "KS 규격 구조화 시드 매핑",
                        "paceflowRelevanceBasis": f"{category} 전용 후보 시드",
                    },
                },
            )
            saved += int(created)
    return saved


def main() -> None:
    h_beam_saved = seed_candidates("H빔", "KS D 3503", H_BEAM_CANDIDATES)
    conduit_saved = seed_candidates("전선관", "KS C IEC 61386-1", CONDUIT_CANDIDATES)
    print(f"H빔 신규 이력 {h_beam_saved}건, 전선관 신규 이력 {conduit_saved}건")
    print("모든 후보는 PaceFlow MVP seed 출처로 저장됨")


if __name__ == "__main__":
    main()
