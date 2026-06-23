from django.db import migrations


def seed_community(apps, schema_editor):
    User = apps.get_model("auth", "User")
    UserProfile = apps.get_model("accounts", "UserProfile")
    CommunityPost = apps.get_model("core", "CommunityPost")

    authors = []
    author_data = [
        ("community-demo-1@paceflow.local", "김현우", "requester", "서울 마포구 현장"),
        ("community-demo-2@paceflow.local", "이서연", "requester", "성동구 프로젝트"),
        ("community-demo-3@paceflow.local", "익명 사용자", "requester", "PaceFlow 현장"),
    ]
    for username, first_name, role, company_name in author_data:
        user, _ = User.objects.get_or_create(
            username=username,
            defaults={"email": username, "first_name": first_name, "password": "!"},
        )
        UserProfile.objects.get_or_create(
            user=user,
            defaults={"role": role, "company_name": company_name},
        )
        authors.append(user)

    posts = [
        {
            "author": authors[0],
            "display_mode": "profile",
            "post_type": "substitute_review",
            "title": "SD400 D13 대신 SD500 D13 검토했던 경험 공유",
            "content": "SD400 D13의 납기가 계속 지연되어 SD500 D13으로 대체 가능 여부를 검토했습니다. 구조 검토를 통해 휨·전단 성능과 상세 간격을 확인했고, 설계사 검토 후 승인까지 무리 없이 진행되었습니다.",
            "material_name": "철근 SD400 D13 → SD500 D13",
            "region": "서울 마포구",
            "status": "승인 검토 완료",
        },
        {
            "author": authors[1],
            "display_mode": "profile",
            "post_type": "supplier_review",
            "title": "동서울전재 전선관 납품 응답 빠름",
            "content": "전선관 16A 경질 500m가 급히 필요했는데, 견적 요청 후 30분 내로 회신을 받았습니다. 재고 확인도 실시간으로 정확하게 안내해 주셔서 납품 일정 조율이 매우 수월했습니다.",
            "material_name": "전선관 16A 경질",
            "supplier_name": "동서울전재",
            "region": "서울 성동구",
            "status": "납품 가능 확인",
        },
        {
            "author": authors[2],
            "display_mode": "anonymous",
            "anonymous_alias": "익명A3F21",
            "post_type": "field_question",
            "title": "경질 전선관과 CD관 대체 가능 범위가 어떻게 되나요?",
            "content": "실내 구간에서 경질 전선관을 CD관으로 대체해도 되는지 기준이 궁금합니다. 노출 조건이나 충격 조건이 있을 경우 승인 기준이 달라지는지 경험 공유 부탁드립니다.",
            "material_name": "경질 전선관 / CD관",
            "region": "서울 강남구",
            "status": "답변 대기",
        },
    ]
    for post in posts:
        CommunityPost.objects.get_or_create(title=post["title"], defaults=post)


def unseed_community(apps, schema_editor):
    CommunityPost = apps.get_model("core", "CommunityPost")
    User = apps.get_model("auth", "User")
    CommunityPost.objects.filter(author__username__startswith="community-demo-").delete()
    User.objects.filter(username__startswith="community-demo-").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
        ("core", "0006_communitypost_communitycontactrequest_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_community, unseed_community),
    ]
