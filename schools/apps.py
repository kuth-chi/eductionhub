from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class SchoolsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'schools'
    
    def ready(self):
        import schools.signals
