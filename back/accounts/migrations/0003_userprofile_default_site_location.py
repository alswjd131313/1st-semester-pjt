from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_userprofile_profile_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="default_site_address",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="default_site_detail_address",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="default_site_zip_no",
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="default_site_latitude",
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="default_site_longitude",
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
    ]
