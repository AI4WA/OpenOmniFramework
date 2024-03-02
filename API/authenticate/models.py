from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from rest_framework_api_key.models import AbstractAPIKey


class Organization(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    org_type = models.CharField(max_length=100, choices=[('research', 'Research'), ('industry', 'Industry')],
                                default='research')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email


class OrgUserAPIKey(AbstractAPIKey):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_keys')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="org_api_key")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username
