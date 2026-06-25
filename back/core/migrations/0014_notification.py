import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0013_demand_draft_status_payload"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Notification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("supplier_inquiry_created", "공급사 문의 도착"),
                            ("supplier_inquiry_status_changed", "공급사 문의 응답"),
                            ("community_comment_created", "커뮤니티 댓글"),
                            ("community_contact_request", "커뮤니티 대화 요청"),
                        ],
                        db_index=True,
                        max_length=60,
                        verbose_name="알림 유형",
                    ),
                ),
                ("title", models.CharField(max_length=120, verbose_name="제목")),
                ("message", models.TextField(verbose_name="내용")),
                ("target_path", models.CharField(blank=True, default="/inquiries", max_length=255, verbose_name="이동 경로")),
                ("event_key", models.CharField(blank=True, db_index=True, max_length=120, verbose_name="중복 방지 키")),
                ("is_read", models.BooleanField(db_index=True, default=False, verbose_name="읽음 여부")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "actor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="sent_notifications",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="발신자",
                    ),
                ),
                (
                    "recipient",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notifications",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="수신자",
                    ),
                ),
                (
                    "related_inquiry",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notifications",
                        to="core.supplierinquiry",
                        verbose_name="관련 문의",
                    ),
                ),
            ],
            options={
                "verbose_name": "알림",
                "verbose_name_plural": "알림 목록",
                "db_table": "notifications",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="notification",
            index=models.Index(fields=["recipient", "is_read", "-created_at"], name="notification_recipient_idx"),
        ),
        migrations.AddConstraint(
            model_name="notification",
            constraint=models.UniqueConstraint(
                condition=~models.Q(event_key=""),
                fields=("recipient", "event_key"),
                name="uniq_notification_recipient_event",
            ),
        ),
    ]
