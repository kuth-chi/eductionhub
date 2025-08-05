from django.core.management.base import BaseCommand
from schools.models.levels import EducationalLevel
from schools.models.school import SchoolType

class Command(BaseCommand):
    help = "Create sample educational levels and school types for testing"

    def handle(self, *args, **options):
        self.stdout.write("Creating sample data...")

        # Create Educational Levels
        levels_data = [
            {
                "level_name": "Primary School",
                "description": "Elementary education (grades 1-6)",
                "order": 1,
                "color": "#4CAF50",
            },
            {
                "level_name": "Secondary School",
                "description": "High school education (grades 7-12)",
                "order": 2,
                "color": "#2196F3",
            },
            {
                "level_name": "College",
                "description": "Undergraduate education",
                "order": 3,
                "color": "#FF9800",
            },
            {
                "level_name": "University",
                "description": "Higher education with graduate programs",
                "order": 4,
                "color": "#9C27B0",
            },
            {
                "level_name": "Vocational School",
                "description": "Technical and vocational training",
                "order": 5,
                "color": "#607D8B",
            },
        ]

        for level_data in levels_data:
            level, created = EducationalLevel.objects.get_or_create(
                level_name=level_data["level_name"], defaults=level_data
            )
            if created:
                self.stdout.write(f"Created educational level: {level.level_name}")
            else:
                self.stdout.write(
                    f"Educational level already exists: {level.level_name}"
                )

        # Create School Types
        types_data = [
            {"type": "Public", "description": "Government-funded schools", "icon": "🏛️"},
            {
                "type": "Private",
                "description": "Privately funded schools",
                "icon": "🏢",
            },
            {
                "type": "International",
                "description": "International curriculum schools",
                "icon": "🌍",
            },
            {
                "type": "Religious",
                "description": "Faith-based educational institutions",
                "icon": "⛪",
            },
            {
                "type": "Charter",
                "description": "Charter schools with special programs",
                "icon": "📚",
            },
        ]

        for type_data in types_data:
            school_type, created = SchoolType.objects.get_or_create(
                type=type_data["type"], defaults=type_data
            )
            if created:
                self.stdout.write(f"Created school type: {school_type.type}")
            else:
                self.stdout.write(f"School type already exists: {school_type.type}")

        self.stdout.write(self.style.SUCCESS("Successfully created sample data!"))
