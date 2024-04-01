from django.contrib.auth.models import AbstractUser, Group
from django.db import models


class Organization(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    org_type = models.CharField(
        max_length=100,
        choices=[("research", "Research"), ("industry", "Industry")],
        default="research",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True
    )
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=100,
        choices=[("org_admin", "ORG Admin"), ("org_editor", "Org Editor"), ("org_viewer", "Org Viewer")],
        default="org_admin",
    )

    def __str__(self):
        return self.email
