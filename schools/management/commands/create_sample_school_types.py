from django.core.management.base import BaseCommand
from schools.models.school import SchoolType


class Command(BaseCommand):
    help = "Create sample school types for testing"

    def handle(self, *args, **options):
        types_data = [
            {
                "type": "Public University",
                "description": "Government-funded university",
                "icon": "university",
            },
            {
                "type": "Private University",
                "description": "Privately-funded university",
                "icon": "graduation-cap",
            },
            {
                "type": "Community College",
                "description": "Two-year community college",
                "icon": "school",
            },
            {
                "type": "Technical Institute",
                "description": "Technical and vocational institute",
                "icon": "tools",
            },
            {
                "type": "Online University",
                "description": "Distance learning institution",
                "icon": "laptop",
            },
            {
                "type": "International School",
                "description": "International curriculum school",
                "icon": "globe",
            },
        ]

        created_count = 0
        for type_data in types_data:
            school_type, created = SchoolType.objects.get_or_create(
                type=type_data["type"], defaults=type_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"Created school type: {school_type.type}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"School type already exists: {school_type.type}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {created_count} new school types")
        )
