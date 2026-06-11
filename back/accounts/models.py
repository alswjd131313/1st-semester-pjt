from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ("requester", "자재 요청자"),
        ("supplier", "공급사"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    company_name = models.CharField(max_length=100)

    class Meta:
        db_table = "user_profiles"

    def __str__(self):
        return f"{self.user.email} ({self.role})"
