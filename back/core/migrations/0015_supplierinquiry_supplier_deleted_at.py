from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0014_notification"),
    ]

    operations = [
        migrations.AddField(
            model_name="supplierinquiry",
            name="supplier_deleted_at",
            field=models.DateTimeField(
                blank=True,
                db_index=True,
                null=True,
                verbose_name="공급사 목록 삭제 일시",
            ),
        ),
    ]
