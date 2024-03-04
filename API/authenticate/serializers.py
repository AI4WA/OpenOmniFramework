from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class APITokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        # Add custom claims
        data['username'] = self.user.username
        data['email'] = self.user.email
        data["org"] = self.user.organization.name if self.user.organization else None
        data["org_id"] = self.user.organization.id if self.user.organization else None
        data["org_type"] = self.user.organization.org_type if self.user.organization else None
        # You can add more custom payload data here

        return data


class APIReturnTokenSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
