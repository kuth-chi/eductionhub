from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class SchoolsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'schools'
    
    def ready(self):
        import schools.signals
                # Import here to avoid circular imports
        from .management.commands.telegram_bot import build_school_index, school_index, school_objs

        # Check if index is already built (e.g., if multiple workers are running)
        # global school_index  # Access the global variable
        if school_index is None:
            logger.info("Building school index on app startup...")
            school_index = build_school_index()
            if not school_index:
                logger.error("Failed to build school index during app startup.")
            else:
                logger.info("School index built successfully.")
