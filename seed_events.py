"""
Quick script to seed event types
Run: python seed_events.py
"""

import os
import django
from django.utils.text import slugify
from event.models import EventCategory, EventType

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

print('🌱 Seeding event categories and types...\n')

# Define categories with their types
categories_data = {
    'Educational': {
        'icon': 'graduation-cap',
        'description': 'Educational events including workshops, seminars, and training sessions',
        'types': [
            {'name': 'Workshop', 'description': 'Hands-on learning sessions'},
            {'name': 'Seminar', 'description': 'Educational presentations and discussions'},
            {'name': 'Training Session', 'description': 'Skill development programs'},
            {'name': 'Conference', 'description': 'Large-scale educational gatherings'},
            {'name': 'Webinar', 'description': 'Online educational sessions'},
            {'name': 'Lecture', 'description': 'Academic presentations'},
            {'name': 'Tutorial', 'description': 'Step-by-step learning sessions'},
        ]
    },
    'Charity': {
        'icon': 'heart',
        'description': 'Charitable events and fundraising activities',
        'types': [
            {'name': 'Fundraiser', 'description': 'Money raising events'},
            {'name': 'Donation Drive', 'description': 'Collection of goods or funds'},
            {'name': 'Charity Run/Walk', 'description': 'Sporting events for charity'},
            {'name': 'Auction', 'description': 'Fundraising through bidding'},
            {'name': 'Gala', 'description': 'Formal charity events'},
            {'name': 'Food Drive', 'description': 'Collection of food items'},
            {'name': 'Blood Donation', 'description': 'Blood collection events'},
        ]
    },
    'Cultural': {
        'icon': 'palette',
        'description': 'Cultural celebrations and artistic events',
        'types': [
            {'name': 'Festival', 'description': 'Cultural celebrations'},
            {'name': 'Concert', 'description': 'Musical performances'},
            {'name': 'Exhibition', 'description': 'Art and cultural displays'},
            {'name': 'Performance', 'description': 'Theater and dance shows'},
            {'name': 'Art Show', 'description': 'Visual arts exhibitions'},
            {'name': 'Cultural Fair', 'description': 'Multicultural celebrations'},
        ]
    },
    'Sports': {
        'icon': 'trophy',
        'description': 'Sports competitions and athletic events',
        'types': [
            {'name': 'Tournament', 'description': 'Competitive sports events'},
            {'name': 'Marathon', 'description': 'Long-distance running events'},
            {'name': 'Competition', 'description': 'Sports contests'},
            {'name': 'Match', 'description': 'Team sports games'},
            {'name': 'Championship', 'description': 'Title-deciding events'},
            {'name': 'Fun Run', 'description': 'Casual running events'},
        ]
    },
    'Health': {
        'icon': 'heartbeat',
        'description': 'Health and wellness events',
        'types': [
            {'name': 'Health Camp', 'description': 'Medical check-up camps'},
            {'name': 'Vaccination Drive', 'description': 'Immunization events'},
            {'name': 'Health Screening', 'description': 'Medical examinations'},
            {'name': 'Wellness Workshop', 'description': 'Health education sessions'},
            {'name': 'Fitness Class', 'description': 'Exercise and fitness activities'},
            {'name': 'Mental Health Session',
                'description': 'Psychological support events'},
        ]
    },
    'Community': {
        'icon': 'users',
        'description': 'Community engagement and social events',
        'types': [
            {'name': 'Meetup', 'description': 'Informal gatherings'},
            {'name': 'Social Gathering', 'description': 'Community social events'},
            {'name': 'Networking Event', 'description': 'Professional connections'},
            {'name': 'Town Hall', 'description': 'Community discussions'},
            {'name': 'Volunteer Event', 'description': 'Community service activities'},
            {'name': 'Clean-up Drive', 'description': 'Environmental cleaning events'},
        ]
    },
    'Business': {
        'icon': 'briefcase',
        'description': 'Business and professional events',
        'types': [
            {'name': 'Conference', 'description': 'Professional gatherings'},
            {'name': 'Trade Show', 'description': 'Industry exhibitions'},
            {'name': 'Product Launch', 'description': 'New product introductions'},
            {'name': 'Business Seminar', 'description': 'Professional development'},
            {'name': 'Pitch Event', 'description': 'Startup presentations'},
            {'name': 'Job Fair', 'description': 'Employment opportunities'},
        ]
    },
    'Environmental': {
        'icon': 'leaf',
        'description': 'Environmental awareness and conservation events',
        'types': [
            {'name': 'Tree Planting', 'description': 'Reforestation activities'},
            {'name': 'Beach Clean-up', 'description': 'Coastal cleaning events'},
            {'name': 'Recycling Drive', 'description': 'Waste collection events'},
            {'name': 'Awareness Campaign', 'description': 'Environmental education'},
            {'name': 'Conservation Event',
                'description': 'Wildlife protection activities'},
        ]
    }
}

CREATED_CATEGORIES = 0
CREATED_TUPES = 0

for category_name, category_info in categories_data.items():
    # Create or get category
    category, created = EventCategory.objects.get_or_create(
        name=category_name,
        defaults={
            'slug': slugify(category_name),
            'icon': category_info['icon'],
            'description': category_info['description'],
            'is_active': True
        }
    )

    if created:
        CREATED_CATEGORIES += 1
        print(f'  ✅ Created category: {category_name}')
    else:
        print(f'  ⚠️  Category exists: {category_name}')

    # Create event types for this category
    for type_data in category_info['types']:
        event_type, type_created = EventType.objects.get_or_create(
            name=type_data['name'],
            category=category,
            defaults={
                'slug': slugify(f"{category_name}-{type_data['name']}"),
                'description': type_data['description'],
                'is_active': True
            }
        )

        if type_created:
            CREATED_TUPES += 1
            print(f'    ✓ {type_data["name"]}')

print('\n✅ Seeding complete!')
print(
    f'  Categories: {CREATED_CATEGORIES} created, {EventCategory.objects.count()} total')
print(f'  Types: {CREATED_TUPES} created, {EventType.objects.count()} total')
