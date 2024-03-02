from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class AuthenticateConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authenticate'

    def ready(self):
        from django.contrib import admin
        from django.apps import apps

        # Ensure the app is ready and models are loaded
        app_config = apps.get_app_config('rest_framework_api_key')

        # Check if the model is registered
        if app_config.models.get('apikey', None):
            # If the model is registered, import it
            api_key_model = app_config.get_model('apikey')

            # Unregister the model
            try:
                admin.site.unregister(api_key_model)
            except admin.sites.NotRegistered:
                # Model was not registered, handle or ignore
                pass
