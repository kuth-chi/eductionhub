"""
Quick script to seed event types
"""
import os

import django

from event.models import EventCategory, EventType

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()


print(f"Total Categories: {EventCategory.objects.count()}")
print(f"Active Categories: {EventCategory.objects.filter(is_active=True).count()}")
print(f"\nTotal Event Types: {EventType.objects.count()}")
print(f"Active Event Types: {EventType.objects.filter(is_active=True).count()}")

print("\n=== Event Types ===")
for t in EventType.objects.filter(is_active=True).select_related('category')[:10]:
    print(f"ID: {t.id}, Name: {t.name}, Category: {t.category.name}")
