from django.core.management.base import BaseCommand
from schools.models.school import SchoolType


class Command(BaseCommand):
    help = "Check current school types in the database"

    def handle(self, *args, **options):
        types = SchoolType.objects.all()

        self.stdout.write(f"Total school types: {types.count()}")
        self.stdout.write("")

        if types.count() > 0:
            self.stdout.write("Current school types:")
            for school_type in types:
                self.stdout.write(
                    f"  - ID: {school_type.pk}, Type: {school_type.type}, "
                    f"Active: {school_type.is_active}"
                )
        else:
            self.stdout.write("No school types found in database.")
            self.stdout.write(
                'Run "python manage.py create_sample_school_types" to create sample data.'
            )

        # Check active types specifically
        active_types = SchoolType.objects.filter(is_active=True)
        self.stdout.write(f"\nActive school types: {active_types.count()}")

        if active_types.count() > 0:
            for school_type in active_types:
                self.stdout.write(f"  - {school_type.type}")
