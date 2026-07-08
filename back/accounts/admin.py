from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "company_name")
    list_filter = ("role",)
    search_fields = ("user__email", "user__first_name", "company_name")
