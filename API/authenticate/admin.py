from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from rest_framework_api_key.admin import APIKeyModelAdmin
from authenticate.models import Organization, User, OrgUserAPIKey
from django.contrib.auth.admin import UserAdmin


@admin.register(User)
class UserAdmin(ImportExportModelAdmin, UserAdmin):
    list_display = ("username", "email", "organization", "is_staff", "is_active")
    search_fields = ("username", "email", "organization__name")
    list_filter = ("is_staff", "is_active", "organization")


@admin.register(Organization)
class OrganizationAdmin(ImportExportModelAdmin):
    list_display = ("name", "org_type", "created_at", "updated_at")
    search_fields = ("name", "org_type")
    list_filter = ("org_type",)


@admin.register(OrgUserAPIKey)
class OrgUserAPIKeyAdmin(ImportExportModelAdmin, APIKeyModelAdmin):
    list_display = ("user", "organization", "created_at", "updated_at")
    search_fields = ("user__username", "organization__name")
    list_filter = ("organization",)


