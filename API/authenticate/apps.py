from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class AuthenticateConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authenticate'
