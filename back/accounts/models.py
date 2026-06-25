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
    profile_image = models.FileField(upload_to="profile_images/", blank=True)
    default_site_address = models.TextField(blank=True)
    default_site_detail_address = models.CharField(max_length=200, blank=True)
    default_site_zip_no = models.CharField(max_length=10, blank=True)
    default_site_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    default_site_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        db_table = "user_profiles"

    def __str__(self):
        return f"{self.user.email} ({self.role})"
