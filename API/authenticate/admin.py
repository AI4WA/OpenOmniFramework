from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from import_export.admin import ImportExportModelAdmin

from authenticate.models import Organization, User


@admin.register(User)
class UserAdmin(ImportExportModelAdmin, UserAdmin):
    list_display = ("username", "email", "organization", "is_staff", "is_active")
    search_fields = ("username", "email", "organization__name")
    list_filter = ("is_staff", "is_active", "organization")
    fieldsets = UserAdmin.fieldsets + (
        ("Other Information", {"fields": ("organization",)}),
    )


@admin.register(Organization)
class OrganizationAdmin(ImportExportModelAdmin):
    list_display = ("name", "org_type", "created_at", "updated_at")
    search_fields = ("name", "org_type")
    list_filter = ("org_type",)
