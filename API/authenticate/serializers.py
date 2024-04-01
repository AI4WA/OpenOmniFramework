from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class APITokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["username"] = user.username
        token["id"] = user.id
        token["first_name"] = user.first_name
        token["last_name"] = user.last_name
        token["org_name"] = user.organization.name if user.organization else None
        token["org_id"] = user.organization.id if user.organization else None
        token["org_type"] = user.organization.org_type if user.organization else None
        # add hasura claims to the token
        token["https://hasura.io/jwt/claims"] = {
            "x-hasura-allowed-roles": ["org_admin", "org_editor", "org_viewer"],
            "x-hasura-default-role": user.role or "org_viewer",
            "x-hasura-role": user.role,
            "x-hasura-user-id": str(user.id),
            "x-hasura-org-id": str(user.organization.id) if user.organization else "",
            "x-hasura-org-type": (
                user.organization.org_type if user.organization else ""
            ),
        }
        return token


class APIReturnTokenSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
