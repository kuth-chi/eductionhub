from django.core.management.base import BaseCommand
from schools.models.online_profile import Platform


class Command(BaseCommand):
    help = "Create sample platforms for testing"

    def handle(self, *args, **options):
        self.stdout.write("Creating sample platforms...")

        # Create Platforms
        platforms_data = [
            {
                "name": "Facebook",
                "short_name": "FB",
                "url": "https://facebook.com",
                "icon": "📘",
            },
            {
                "name": "Twitter",
                "short_name": "TW",
                "url": "https://twitter.com",
                "icon": "🐦",
            },
            {
                "name": "Instagram",
                "short_name": "IG",
                "url": "https://instagram.com",
                "icon": "📷",
            },
            {
                "name": "LinkedIn",
                "short_name": "LI",
                "url": "https://linkedin.com",
                "icon": "💼",
            },
            {
                "name": "YouTube",
                "short_name": "YT",
                "url": "https://youtube.com",
                "icon": "📺",
            },
            {
                "name": "Website",
                "short_name": "WEB",
                "url": "",
                "icon": "🌐",
            },
            {
                "name": "Telegram",
                "short_name": "TG",
                "url": "https://telegram.org",
                "icon": "📱",
            },
        ]

        for platform_data in platforms_data:
            platform, created = Platform.objects.get_or_create(
                name=platform_data["name"], defaults=platform_data
            )
            if created:
                self.stdout.write(f"Created platform: {platform.name}")
            else:
                self.stdout.write(f"Platform already exists: {platform.name}")

        self.stdout.write(self.style.SUCCESS("Successfully created sample platforms!"))
