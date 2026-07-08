from django.db import migrations, models


def classify_materials(apps, schema_editor):
    Material = apps.get_model("core", "Material")

    for material in Material.objects.all().iterator():
        name = material.name or ""
        grade = (material.ks_grade or "").upper()
        group = ""
        subtype = "other"

        if name == "철근":
            group = "rebar"
            subtype = "round_rebar" if grade.startswith("SR") else "deformed_rebar"
        elif name == "H빔":
            group = "shape_steel"
            subtype = "h_beam"
        elif name == "시멘트":
            group = "cement"
            if grade.startswith("1종"):
                subtype = "ordinary_portland"
            elif grade.startswith("3종"):
                subtype = "high_early_strength"
        elif name == "단열재":
            group = "insulation"
            if "EPS" in grade:
                subtype = "eps"
            elif "XPS" in grade:
                subtype = "xps"
            elif "PUR" in grade or "우레탄" in grade:
                subtype = "rigid_polyurethane"
            elif "글라스울" in grade or "유리면" in grade:
                subtype = "glass_wool"
        elif name == "전선관":
            group = "electrical_conduit"
            if "CD관" in grade:
                subtype = "cd_conduit"
            elif "PF관" in grade:
                subtype = "pf_conduit"
            elif "가요" in grade:
                subtype = "flexible_conduit"
            else:
                subtype = "rigid_conduit"

        material.material_group = group
        material.material_subtype = subtype if group else ""
        material.save(update_fields=["material_group", "material_subtype"])


class Migration(migrations.Migration):
    dependencies = [("core", "0002_demand_owner_suppliermaterialregistration")]

    operations = [
        migrations.AddField(
            model_name="material",
            name="material_group",
            field=models.CharField(
                blank=True,
                choices=[
                    ("rebar", "철근"),
                    ("shape_steel", "형강·강재"),
                    ("cement", "시멘트"),
                    ("insulation", "단열재"),
                    ("electrical_conduit", "전기 배관재"),
                ],
                db_index=True,
                max_length=30,
                verbose_name="자재 대분류",
            ),
        ),
        migrations.AddField(
            model_name="material",
            name="material_subtype",
            field=models.CharField(
                blank=True,
                choices=[
                    ("deformed_rebar", "이형철근"),
                    ("round_rebar", "원형철근"),
                    ("h_beam", "H형강"),
                    ("angle", "ㄱ형강"),
                    ("channel", "ㄷ형강"),
                    ("square_tube", "각형강관"),
                    ("steel_plate", "강판"),
                    ("ordinary_portland", "보통 포틀랜드 시멘트"),
                    ("blast_furnace_slag", "고로슬래그 시멘트"),
                    ("high_early_strength", "조강 포틀랜드 시멘트"),
                    ("eps", "EPS"),
                    ("xps", "XPS"),
                    ("glass_wool", "글라스울"),
                    ("rigid_polyurethane", "경질 우레탄폼"),
                    ("rigid_conduit", "경질 전선관"),
                    ("flexible_conduit", "가요 전선관"),
                    ("cd_conduit", "CD관"),
                    ("pf_conduit", "PF관"),
                    ("other", "기타/검토 필요"),
                ],
                db_index=True,
                max_length=30,
                verbose_name="세부 품목",
            ),
        ),
        migrations.RunPython(classify_materials, migrations.RunPython.noop),
    ]
