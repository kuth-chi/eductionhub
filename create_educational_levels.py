#!/usr/bin/env python
"""
Script to create sample educational levels for testing the frontend dropdown
"""

from schools.models.levels import EducationalLevel
import os

import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()


def create_educational_levels():
    """Create sample educational levels"""

    levels_data = [
        {
            'level_name': 'Primary Education',
            'badge': 'PE',
            'color': '4CAF50',
            'description': 'Elementary school education covering grades 1-6',
            'order': 1
        },
        {
            'level_name': 'Secondary Education',
            'badge': 'SE',
            'color': '2196F3',
            'description': 'Middle and high school education covering grades 7-12',
            'order': 2
        },
        {
            'level_name': 'Higher Education',
            'badge': 'HE',
            'color': '9C27B0',
            'description': 'University and college level education',
            'order': 3
        },
        {
            'level_name': 'Undergraduate',
            'badge': 'UG',
            'color': 'FF9800',
            'description': 'Bachelor\'s degree level programs',
            'order': 4
        },
        {
            'level_name': 'Graduate',
            'badge': 'GR',
            'color': 'F44336',
            'description': 'Master\'s and doctoral degree programs',
            'order': 5
        },
        {
            'level_name': 'Postgraduate',
            'badge': 'PG',
            'color': '795548',
            'description': 'Advanced graduate programs and research',
            'order': 6
        },
        {
            'level_name': 'Vocational Training',
            'badge': 'VT',
            'color': '607D8B',
            'description': 'Technical and professional skills training',
            'order': 7
        },
        {
            'level_name': 'Certification Programs',
            'badge': 'CP',
            'color': '3F51B5',
            'description': 'Professional certification and continuing education',
            'order': 8
        }
    ]

    created_count = 0

    for level_data in levels_data:
        level, created = EducationalLevel.objects.get_or_create(
            level_name=level_data['level_name'],
            defaults=level_data
        )

        if created:
            print(f"✓ Created: {level.level_name}")
            created_count += 1
        else:
            print(f"- Already exists: {level.level_name}")

    print(f"\nSummary: Created {created_count} new educational levels")

    # Show all active levels
    active_levels = EducationalLevel.objects.filter(
        is_active=True, is_deleted=False).order_by('order')
    print(f"\nTotal active educational levels: {active_levels.count()}")

    for level in active_levels:
        print(
            f"- {level.level_name} (UUID: {level.uuid}, Badge: {level.badge or 'No badge'})")


if __name__ == '__main__':
    create_educational_levels()
