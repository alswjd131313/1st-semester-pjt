import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0012_categorycontracthistory"),
    ]

    operations = [
        migrations.AddField(
            model_name="demand",
            name="status",
            field=models.CharField(
                choices=[
                    ("draft", "임시 저장"),
                    ("submitted", "제출됨"),
                    ("recommended", "추천 완료"),
                ],
                db_index=True,
                default="submitted",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="demand",
            name="draft_payload",
            field=models.JSONField(blank=True, default=dict, verbose_name="요청 원본 데이터"),
        ),
        migrations.AlterField(
            model_name="demand",
            name="site_name",
            field=models.CharField(blank=True, max_length=200, verbose_name="현장명"),
        ),
        migrations.AlterField(
            model_name="demand",
            name="site_lat",
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True, verbose_name="현장 위도"),
        ),
        migrations.AlterField(
            model_name="demand",
            name="site_lng",
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True, verbose_name="현장 경도"),
        ),
        migrations.AlterField(
            model_name="demand",
            name="quantity",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=15,
                null=True,
                validators=[django.core.validators.MinValueValidator(0)],
                verbose_name="필요 수량 (kg)",
            ),
        ),
        migrations.AlterField(
            model_name="demand",
            name="deadline",
            field=models.DateField(blank=True, null=True, verbose_name="납기 기한"),
        ),
    ]
