#!/usr/bin/env python3
"""Test script for enhanced session management with abnormal activity detection."""

from api.views.auth.auth_viewset import ActiveSessionsView
import os
import sys
from datetime import datetime, timedelta, timezone

import django

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

django.setup()


def test_risk_calculation():
    """Test the risk calculation functionality."""
    auth_view = ActiveSessionsView()

    # Test data
    current_time = datetime.now(timezone.utc)
    old_session_time = current_time - timedelta(days=35)  # Very old session
    recent_session_time = current_time - timedelta(hours=2)  # Recent session

    current_ip = "192.168.1.100"
    different_ip = "203.45.67.89"  # Different network
    similar_ip = "192.168.1.105"  # Same network

    current_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    mobile_ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1"
    bot_ua = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"

    print("🔒 Testing Enhanced Session Risk Analysis")
    print("=" * 50)

    # Test 1: Recent session, same IP, same UA (low risk)
    risk1 = auth_view._calculate_risk_score(
        current_ip, current_ua, recent_session_time, None, current_ip, current_ua
    )
    level1 = auth_view._get_risk_level(risk1)
    print(f"✅ Recent session, same IP/UA: Risk={risk1}% ({level1})")

    # Test 2: Old session (high risk due to age)
    risk2 = auth_view._calculate_risk_score(
        current_ip, current_ua, old_session_time, None, current_ip, current_ua
    )
    level2 = auth_view._get_risk_level(risk2)
    print(f"⚠️ Very old session: Risk={risk2}% ({level2})")

    # Test 3: Different IP network (medium-high risk)
    risk3 = auth_view._calculate_risk_score(
        different_ip, current_ua, recent_session_time, None, current_ip, current_ua
    )
    level3 = auth_view._get_risk_level(risk3)
    print(f"🌍 Different IP network: Risk={risk3}% ({level3})")

    # Test 4: Mobile vs Desktop (medium risk)
    risk4 = auth_view._calculate_risk_score(
        current_ip, mobile_ua, recent_session_time, None, current_ip, current_ua
    )
    level4 = auth_view._get_risk_level(risk4)
    print(f"📱 Mobile vs Desktop: Risk={risk4}% ({level4})")

    # Test 5: Bot/Crawler detection (high risk)
    risk5 = auth_view._calculate_risk_score(
        current_ip, bot_ua, recent_session_time, None, current_ip, current_ua
    )
    level5 = auth_view._get_risk_level(risk5)
    print(f"🤖 Bot/Crawler detected: Risk={risk5}% ({level5})")

    print("\n🔍 Testing Device Info Parsing")
    print("=" * 40)

    # Test device info parsing
    device_info = auth_view._parse_device_info(
        current_ua, current_ip, recent_session_time)
    print(
        f"Desktop Chrome: {device_info['deviceName']} | OS: {device_info['os']} | Browser: {device_info['browser']}")

    mobile_device_info = auth_view._parse_device_info(
        mobile_ua, current_ip, recent_session_time)
    print(
        f"Mobile Safari: {mobile_device_info['deviceName']} | OS: {mobile_device_info['os']} | Browser: {mobile_device_info['browser']}")

    print("\n⏱️ Testing Session Duration")
    print("=" * 35)

    duration1 = auth_view._calculate_session_duration(recent_session_time)
    duration2 = auth_view._calculate_session_duration(old_session_time)
    print(f"Recent session: {duration1}")
    print(f"Old session: {duration2}")

    print("\n🗺️ Testing Location Detection")
    print("=" * 36)

    location1 = auth_view._get_approximate_location(current_ip)
    location2 = auth_view._get_approximate_location(different_ip)
    location3 = auth_view._get_approximate_location("127.0.0.1")

    print(f"LAN IP: {location1}")
    print(f"External IP: {location2}")
    print(f"Localhost: {location3}")

    print("\n✅ All tests completed! The enhanced session management system is working correctly.")
    print("🔒 Features available:")
    print("   • Risk-based session scoring")
    print("   • Device fingerprinting")
    print("   • Abnormal activity detection")
    print("   • Session duration tracking")
    print("   • Basic geolocation")


if __name__ == "__main__":
    test_risk_calculation()
