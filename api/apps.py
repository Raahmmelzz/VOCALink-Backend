from django.apps import AppConfig

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    # Add this ready function to load your signals!
    def ready(self):
        import api.signals