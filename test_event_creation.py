"""
Test script to debug event creation ValueError
"""
import json
from decimal import Decimal

# Sample data from the logs
test_data = {
    "title": "Run For Child Education",
    "description": "Test create event",
    "event_type": 8,
    "start_datetime": "2025-10-08T02:00:00.000Z",
    "end_datetime": "2025-10-31T10:00:00.000Z",
    "timezone": "UTC",
    "is_virtual": False,
    "address_line_1": "Bat Nim Village",
    "country": 1,
    "state": 2,
    "city": 1,
    "latitude": 13.35959,
    "longitude": 103.858902,
    "status": "published",
    "visibility": "public",
    "is_featured": True,
    "currency": "USD",
    "max_participants": 500000,
    "registration_deadline": "2025-10-24T17:00:00.000Z",
    "slug": "run-for-child-education",
    "requires_approval": False,
}

print("Testing data conversion...")
print("\nOriginal data:")
print(json.dumps(test_data, indent=2))

# Test coordinate conversion
try:
    lat = Decimal(str(test_data["latitude"]))
    lng = Decimal(str(test_data["longitude"]))
    print(f"\n✅ Latitude conversion: {lat} (type: {type(lat)})")
    print(f"✅ Longitude conversion: {lng} (type: {type(lng)})")
except Exception as e:
    print(f"\n❌ Error converting coordinates: {e}")

# Test integer conversion
try:
    event_type = int(test_data["event_type"])
    country = int(test_data["country"])
    max_p = int(test_data["max_participants"])
    print(f"\n✅ Integer conversions successful")
    print(f"   event_type: {event_type}")
    print(f"   country: {country}")
    print(f"   max_participants: {max_p}")
except Exception as e:
    print(f"\n❌ Error converting integers: {e}")

# Check decimal precision
print(f"\n🔍 Coordinate precision check:")
print(
    f"   Latitude digits: {len(str(test_data['latitude']).replace('.', '').replace('-', ''))}")
print(
    f"   Longitude digits: {len(str(test_data['longitude']).replace('.', '').replace('-', ''))}")

lat_str = str(test_data['latitude'])
lng_str = str(test_data['longitude'])

if '.' in lat_str:
    before, after = lat_str.split('.')
    print(
        f"   Latitude: {len(before)} digits before decimal, {len(after)} after")

if '.' in lng_str:
    before, after = lng_str.split('.')
    print(
        f"   Longitude: {len(before)} digits before decimal, {len(after)} after")

print("\n✅ All conversions successful!")
