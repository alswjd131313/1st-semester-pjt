from django.db import migrations


STANDARDS = [
    {
        "key": "d3502",
        "code": "KS D 3502",
        "revision": "2022",
        "title": "열간 압연 형강의 모양·치수·무게 및 그 허용차",
        "material_group": "shape_steel",
        "scope_note": "H형강, ㄱ형강, ㄷ형강 등의 공칭 치수, 단위 무게, 단면 성능과 허용차",
        "verification_status": "partial",
    },
    {
        "key": "d3503",
        "code": "KS D 3503",
        "revision": "2018",
        "title": "일반 구조용 압연 강재",
        "material_group": "shape_steel",
        "scope_note": "SS 강종별 화학 성분과 두께 조건별 항복강도, 인장강도 및 연신율",
        "verification_status": "verified",
    },
    {
        "key": "d3568",
        "code": "KS D 3568",
        "revision": "2025",
        "title": "일반 구조용 각형 강관",
        "material_group": "shape_steel",
        "material_subtype": "square_tube",
        "scope_note": "정사각형·직사각형 강관의 SRT 강종, 치수, 단위 무게, 기계적 성질과 허용차",
        "verification_status": "partial",
    },
    {
        "key": "l5210",
        "code": "KS L 5210",
        "revision": "2017",
        "title": "고로 슬래그 시멘트",
        "material_group": "cement",
        "material_subtype": "blast_furnace_slag",
        "scope_note": "고로 슬래그 함유율에 따른 1·2·3종과 화학·물리 성능",
        "verification_status": "verified",
    },
    {
        "key": "l9102",
        "code": "KS L 9102",
        "revision": "2026",
        "title": "인조 광물섬유 단열재",
        "material_group": "insulation",
        "material_subtype": "glass_wool",
        "scope_note": "미네랄울·글라스울의 종류, 밀도, 열전도도, 열간 수축 온도, 치수와 수분 성능",
        "verification_status": "partial",
    },
]


SECTION_PROFILES = [
    ("d3502", "h_beam", "H-100x100x6x8", {"H": 100, "B": 100, "t1": 6, "t2": 8, "r": 10}, 17.2, 21.90, "부표 9"),
    ("d3502", "h_beam", "H-200x200x8x12", {"H": 200, "B": 200, "t1": 8, "t2": 12, "r": 13}, 49.9, 63.53, "부표 9"),
    ("d3502", "h_beam", "H-300x300x10x15", {"H": 300, "B": 300, "t1": 10, "t2": 15, "r": 18}, 94.0, 119.8, "부표 9"),
    ("d3502", "h_beam", "H-400x200x8x13", {"H": 400, "B": 200, "t1": 8, "t2": 13, "r": 16}, 66.0, 84.12, "부표 9"),
    ("d3502", "angle", "L-50x50x4", {"A": 50, "B": 50, "t": 4, "r1": 6.5, "r2": 3}, 3.06, 3.892, "부표 1"),
    ("d3502", "angle", "L-75x75x6", {"A": 75, "B": 75, "t": 6, "r1": 8.5, "r2": 4}, 6.85, 8.727, "부표 1"),
    ("d3502", "channel", "C-100x50x5x7.5", {"H": 100, "B": 50, "t1": 5, "t2": 7.5, "r1": 8, "r2": 4}, 9.36, 11.92, "부표 5"),
    ("d3568", "square_tube", "100x100x4.0", {"A": 100, "B": 100, "t": 4.0}, 11.7, 14.95, "부표 1"),
    ("d3568", "square_tube", "200x200x6.0", {"A": 200, "B": 200, "t": 6.0}, 35.8, 59.79, "부표 1"),
    ("d3568", "rectangular_tube", "100x50x3.2", {"A": 100, "B": 50, "t": 3.2}, 7.01, 8.927, "부표 1"),
    ("d3568", "rectangular_tube", "200x100x6.0", {"A": 200, "B": 100, "t": 6.0}, 26.4, 33.63, "부표 1"),
]


def requirement(standard, grade, code, name, value_type, source, *, subtype="", minimum=None, maximum=None, text="", unit="", condition=None, priority=100):
    return {
        "standard": standard,
        "material_subtype": subtype,
        "grade": grade,
        "property_code": code,
        "property_name": name,
        "value_type": value_type,
        "min_value": minimum,
        "max_value": maximum,
        "text_value": text,
        "unit": unit,
        "condition": condition or {},
        "source_location": source,
        "display_priority": priority,
    }


def build_requirements(standards):
    rows = []

    steel_grades = {
        "SS235": ([235, 225, 205, 195], 330, 450),
        "SS275": ([275, 265, 245, 235], 410, 550),
        "SS315": ([315, 305, 295, 275], 490, 630),
        "SS410": ([410, 400, None, None], 540, None),
        "SS450": ([450, 440, None, None], 590, None),
        "SS550": ([550, 540, None, None], 690, None),
    }
    thickness_ranges = [(None, 16), (16, 40), (40, 100), (100, None)]
    for grade, (yield_values, tensile_min, tensile_max) in steel_grades.items():
        for value, (lower, upper) in zip(yield_values, thickness_ranges):
            if value is None:
                continue
            condition = {"thickness_mm": {}}
            if lower is not None:
                condition["thickness_mm"]["gt"] = lower
            if upper is not None:
                condition["thickness_mm"]["lte"] = upper
            rows.append(requirement(standards["d3503"], grade, "yield_strength", "항복강도", "minimum", "표 3", minimum=value, unit="MPa", condition=condition, priority=10))
        rows.append(requirement(standards["d3503"], grade, "tensile_strength", "인장강도", "range" if tensile_max else "minimum", "표 3", minimum=tensile_min, maximum=tensile_max, unit="MPa", condition={"thickness_mm": {"lte": 40}}, priority=20))

    pipe_grades = {
        "SRT275": (275, 410, 23),
        "SRT355": (355, 500, 23),
        "SRT410": (410, 540, 20),
        "SRT450": (450, 590, 20),
        "SRT550": (550, 690, 20),
    }
    for grade, (yield_min, tensile_min, elongation_min) in pipe_grades.items():
        rows.extend([
            requirement(standards["d3568"], grade, "yield_strength", "항복강도", "minimum", "표 3", subtype="square_tube", minimum=yield_min, unit="MPa", priority=10),
            requirement(standards["d3568"], grade, "tensile_strength", "인장강도", "minimum", "표 3", subtype="square_tube", minimum=tensile_min, unit="MPa", priority=20),
            requirement(standards["d3568"], grade, "elongation", "연신율", "minimum", "표 3", subtype="square_tube", minimum=elongation_min, unit="%", condition={"test_piece": "No.5"}, priority=30),
        ])

    cement_types = {
        "1종": (5, 30, 3000, 45, 7, (12.5, 22.5, 42.5)),
        "2종": (30, 60, 3000, 60, 10, (10.0, 17.5, 42.5)),
        "3종": (60, 70, 3300, 60, 10, (7.5, 15.0, 40.0)),
    }
    for grade, (slag_min, slag_max, fineness, initial, final, strengths) in cement_types.items():
        rows.extend([
            requirement(standards["l5210"], grade, "slag_content", "고로 슬래그 함유율", "range", "표 1", subtype="blast_furnace_slag", minimum=slag_min, maximum=slag_max, unit="%", condition={"lower_exclusive": True}, priority=10),
            requirement(standards["l5210"], grade, "fineness", "분말도", "minimum", "표 3", subtype="blast_furnace_slag", minimum=fineness, unit="cm2/g", priority=20),
            requirement(standards["l5210"], grade, "initial_setting", "초결", "minimum", "표 3", subtype="blast_furnace_slag", minimum=initial, unit="min", priority=30),
            requirement(standards["l5210"], grade, "final_setting", "종결", "maximum", "표 3", subtype="blast_furnace_slag", maximum=final, unit="h", priority=40),
        ])
        for age, strength in zip((3, 7, 28), strengths):
            rows.append(requirement(standards["l5210"], grade, "compressive_strength", "압축강도", "minimum", "표 3", subtype="blast_furnace_slag", minimum=strength, unit="MPa", condition={"age_days": age}, priority=50 + age))

    glass_wool = {
        "일반": (None, None, 0.035, 0.042, 400),
        "보온판 24K": (22, 27, 0.037, 0.048, 300),
        "보온판 32K": (28, 36, 0.036, 0.045, 300),
        "보온판 40K": (36, 44, 0.035, 0.043, 350),
        "보온판 64K": (58, 70, 0.034, 0.042, 400),
        "보온판 80K": (73, 87, 0.034, 0.042, 400),
    }
    for grade, (density_min, density_max, lambda_20, lambda_70, shrink_temp) in glass_wool.items():
        if density_min is not None:
            rows.append(requirement(standards["l9102"], grade, "density", "밀도", "range", "표 2-2", subtype="glass_wool", minimum=density_min, maximum=density_max, unit="kg/m3", priority=10))
        rows.extend([
            requirement(standards["l9102"], grade, "thermal_conductivity", "열전도도", "maximum", "표 2-2", subtype="glass_wool", maximum=lambda_20, unit="W/(m·K)", condition={"mean_temperature_c": 20}, priority=20),
            requirement(standards["l9102"], grade, "thermal_conductivity", "열전도도", "maximum", "표 2-2", subtype="glass_wool", maximum=lambda_70, unit="W/(m·K)", condition={"mean_temperature_c": 70}, priority=21),
            requirement(standards["l9102"], grade, "hot_shrinkage_temperature", "열간 수축 온도", "minimum", "표 2-2", subtype="glass_wool", minimum=shrink_temp, unit="°C", priority=30),
        ])
    rows.extend([
        requirement(standards["l9102"], "수분 노출 제품", "short_term_water_absorption", "단기흡수성", "maximum", "7.11.1", subtype="glass_wool", maximum=1.0, unit="kg/m2", priority=40),
        requirement(standards["l9102"], "수분 노출 제품", "long_term_water_absorption", "장기흡수성", "maximum", "7.11.2", subtype="glass_wool", maximum=3.0, unit="kg/m2", priority=41),
    ])
    return rows


def seed_ks_evidence(apps, schema_editor):
    KSStandard = apps.get_model("core", "KSStandard")
    KSRequirement = apps.get_model("core", "KSRequirement")
    KSSectionProfile = apps.get_model("core", "KSSectionProfile")

    standards = {}
    for data in STANDARDS:
        key = data["key"]
        payload = {field: value for field, value in data.items() if field != "key"}
        standard, _ = KSStandard.objects.update_or_create(
            code=payload.pop("code"),
            revision=payload.pop("revision"),
            defaults=payload,
        )
        standards[key] = standard

    KSRequirement.objects.bulk_create([
        KSRequirement(**data) for data in build_requirements(standards)
    ])
    KSSectionProfile.objects.bulk_create([
        KSSectionProfile(
            standard=standards[standard_key],
            profile_type=profile_type,
            designation=designation,
            dimensions=dimensions,
            unit_mass_kg_m=unit_mass,
            area_cm2=area,
            source_location=source,
        )
        for standard_key, profile_type, designation, dimensions, unit_mass, area, source in SECTION_PROFILES
    ])


def unseed_ks_evidence(apps, schema_editor):
    KSStandard = apps.get_model("core", "KSStandard")
    pairs = [(item["code"], item["revision"]) for item in STANDARDS]
    for code, revision in pairs:
        KSStandard.objects.filter(code=code, revision=revision).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0004_ksstandard_kssectionprofile_ksrequirement"),
    ]

    operations = [
        migrations.RunPython(seed_ks_evidence, unseed_ks_evidence),
    ]
