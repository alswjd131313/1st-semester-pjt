from datetime import timedelta

from django.db import migrations
from django.utils import timezone


def stagger_demo_times(apps, schema_editor):
    CommunityPost = apps.get_model("core", "CommunityPost")
    now = timezone.now()
    demo_times = {
        "SD400 D13 대신 SD500 D13 검토했던 경험 공유": now - timedelta(hours=2),
        "동서울전재 전선관 납품 응답 빠름": now - timedelta(hours=4),
        "경질 전선관과 CD관 대체 가능 범위가 어떻게 되나요?": now - timedelta(days=1),
    }
    for title, created_at in demo_times.items():
        CommunityPost.objects.filter(title=title).update(created_at=created_at, updated_at=created_at)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0008_communitycomment_anonymous_alias_and_more"),
    ]

    operations = [
        migrations.RunPython(stagger_demo_times, migrations.RunPython.noop),
    ]
