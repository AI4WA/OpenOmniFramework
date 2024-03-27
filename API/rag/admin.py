from django.contrib import admin

# Register your models here.
from import_export.admin import ImportExportModelAdmin

from rag.models import Patient


@admin.register(Patient)
class PatientAdmin(ImportExportModelAdmin):
    list_display = ("uid", "routine",
                    "family_condition",
                    "health_condition",
                    "diet_preference",
                    "hobby",
                    "personality",
                    "additional_info")
    search_fields = ("routine", "family_condition")
    list_filter = ("routine",
                   "family_condition",
                   "health_condition",
                   "diet_preference",
                   "hobby",
                   "personality",
                   "additional_info")
