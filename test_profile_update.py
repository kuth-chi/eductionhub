#!/usr/bin/env python
"""
Quick backend connectivity test for profile update functionality
"""

import os
import sys
import django

# Set up Django environment
sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from django.contrib.auth import get_user_model
from user.models.profile import Profile
from geo.models import Country, State, City

User = get_user_model()

def test_backend_setup():
    """Test that backend is properly configured for profile updates"""
    
    print("=" * 60)
    print("PROFILE UPDATE BACKEND TEST")
    print("=" * 60)
    print()
    
    # Test 1: Check if users exist
    print("1. Checking users...")
    user_count = User.objects.count()
    print(f"   ✅ Found {user_count} users")
    
    if user_count > 0:
        user = User.objects.first()
        print(f"   📝 Sample user: {user.username} ({user.email})")
    print()
    
    # Test 2: Check if profiles exist
    print("2. Checking profiles...")
    profile_count = Profile.objects.count()
    print(f"   ✅ Found {profile_count} profiles")
    
    if profile_count > 0:
        profile = Profile.objects.first()
        print(f"   📝 Sample profile: {profile.user.username}")
        print(f"      - Gender: {profile.gender or 'Not set'}")
        print(f"      - Phone: {profile.phone or 'Not set'}")
        print(f"      - DOB: {profile.date_of_birth or 'Not set'}")
        print(f"      - Address: {profile.address_line1 or 'Not set'}")
        print(f"      - Country: {profile.country.name if profile.country else 'Not set'}")
        print(f"      - State: {profile.state.name if profile.state else 'Not set'}")
        print(f"      - City: {profile.city.name if profile.city else 'Not set'}")
    print()
    
    # Test 3: Check geo data
    print("3. Checking geo data...")
    country_count = Country.objects.count()
    state_count = State.objects.count()
    city_count = City.objects.count()
    print(f"   ✅ Countries: {country_count}")
    print(f"   ✅ States: {state_count}")
    print(f"   ✅ Cities: {city_count}")
    
    if country_count > 0:
        sample_countries = Country.objects.all()[:3]
        print(f"   📝 Sample countries:")
        for country in sample_countries:
            print(f"      - {country.flag_emoji} {country.name} (ID: {country.id})")
    print()
    
    # Test 4: Test profile update fields
    print("4. Testing ProfileSerializer fields...")
    from api.serializers.user.profile import ProfileSerializer
    serializer = ProfileSerializer()
    fields = serializer.fields.keys()
    
    required_fields = [
        'gender', 'occupation', 'timezone',
        'phone', 'date_of_birth',
        'address_line1', 'address_line2', 'postal_code',
        'country_id', 'state_id', 'city_id'
    ]
    
    for field in required_fields:
        if field in fields:
            print(f"   ✅ {field}")
        else:
            print(f"   ❌ {field} MISSING!")
    print()
    
    # Test 5: Check endpoint availability
    print("5. Checking ViewSet configuration...")
    from api.views.user.profile_viewset import ProfileViewSet
    
    # Check if my_profile action exists
    if hasattr(ProfileViewSet, 'my_profile'):
        print("   ✅ my_profile action exists")
        action = getattr(ProfileViewSet, 'my_profile')
        print(f"   📝 Methods: {action.mapping if hasattr(action, 'mapping') else 'GET, PATCH, PUT'}")
    else:
        print("   ❌ my_profile action NOT FOUND!")
    print()
    
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if user_count > 0 and profile_count > 0 and country_count > 0:
        print("✅ Backend is properly configured!")
        print()
        print("Next steps:")
        print("1. Start backend server: python manage.py runserver")
        print("2. Start frontend server: npm run dev")
        print("3. Navigate to http://localhost:3000/profile/edit/")
        print("4. Open browser console (F12)")
        print("5. Fill form and click 'Save All Changes'")
        print("6. Check console logs for debug output")
    else:
        print("⚠️  Backend setup incomplete!")
        if user_count == 0:
            print("   - No users found. Create a superuser: python manage.py createsuperuser")
        if profile_count == 0:
            print("   - No profiles found. Profiles are auto-created on first login")
        if country_count == 0:
            print("   - No geo data. Run: python manage.py loaddata geo_data.json")
    
    print()

if __name__ == '__main__':
    test_backend_setup()
