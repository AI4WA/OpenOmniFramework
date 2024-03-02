from rest_framework import permissions
from rest_framework_api_key.permissions import HasAPIKey

import logging

logger = logging.getLogger(__name__)


class HasAPIKeyOrIsAuthenticated(permissions.BasePermission):
    """
    Custom permission to allow access to either authenticated users or holders of a valid API key.
    """

    def has_permission(self, request, view):
        logger.info("Checking permissions")
        has_api_key = HasAPIKey().has_permission(request, view)
        is_authenticated = permissions.IsAuthenticated().has_permission(request, view)
        return has_api_key or is_authenticated
