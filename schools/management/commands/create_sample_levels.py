from django.core.management.base import BaseCommand
from schools.models.levels import EducationalLevel


class Command(BaseCommand):
    help = "Create sample educational levels for testing"

    def handle(self, *args, **options):
        levels_data = [
            {
                "level_name": "Primary Education",
                "badge": "Primary",
                "color": "4CAF50",
                "description": "Basic primary education level",
                "order": 1,
            },
            {
                "level_name": "Secondary Education",
                "badge": "Secondary",
                "color": "2196F3",
                "description": "Secondary education level",
                "order": 2,
            },
            {
                "level_name": "Higher Education",
                "badge": "Higher",
                "color": "FF9800",
                "description": "University and college level education",
                "order": 3,
            },
            {
                "level_name": "Graduate Education",
                "badge": "Graduate",
                "color": "9C27B0",
                "description": "Masters and PhD level education",
                "order": 4,
            },
            {
                "level_name": "Vocational Training",
                "badge": "Vocational",
                "color": "607D8B",
                "description": "Technical and vocational training",
                "order": 5,
            },
        ]

        created_count = 0
        for level_data in levels_data:
            level, created = EducationalLevel.objects.get_or_create(
                level_name=level_data["level_name"], defaults=level_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"Created educational level: {level.level_name}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Educational level already exists: {level.level_name}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created {created_count} new educational levels"
            )
        )
