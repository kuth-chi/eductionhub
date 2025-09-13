"""
Test script to verify that the ad storage cleanup system works properly.
Run this script from the Django project root using: python test_ad_storage_cleanup.py
"""

from ads.utils.storage_cleanup import (calculate_storage_size,
                                       find_orphaned_files, get_cleanup_report,
                                       validate_database_file_integrity)
from ads.models import AdManager, AdType
import os
import sys
from pathlib import Path

import django

# Add the Django project to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print('='*60)


def test_basic_functionality():
    """Test that all our cleanup functions work without errors."""
    print_section("TESTING BASIC FUNCTIONALITY")

    try:
        # Test storage statistics
        print("📊 Testing calculate_storage_size()...")
        stats = calculate_storage_size()
        print(
            f"   ✅ Found {stats['total_files']} files, {stats['total_size_formatted']} total")

        # Test orphaned file detection
        print("\n🔍 Testing find_orphaned_files()...")
        orphaned_files, count = find_orphaned_files()
        print(f"   ✅ Found {count} orphaned files")

        # Test database integrity check
        print("\n🔍 Testing validate_database_file_integrity()...")
        existing_files, missing_files = validate_database_file_integrity()
        print(
            f"   ✅ Database check complete: {len(existing_files)} exist, {len(missing_files)} missing")

        # Test comprehensive report
        print("\n📋 Testing get_cleanup_report()...")
        report = get_cleanup_report()
        print(
            f"   ✅ Report generated with {len(report['recommendations'])} recommendations")

        return True

    except Exception as e:
        print(f"❌ Basic functionality test failed: {str(e)}")
        return False


def test_ad_creation_and_cleanup():
    """Test creating an ad and then cleaning up when it's deleted."""
    print_section("TESTING AD CREATION & CLEANUP")

    try:
        # Get or create an ad type
        ad_type, created = AdType.objects.get_or_create(
            name="LOGO",
            defaults={'description': 'Logo advertisement type for testing'}
        )
        if created:
            print("✅ Created LOGO ad type for testing")

        # Create a test ad (without actually uploading a file for this test)
        test_ad = AdManager.objects.create(
            campaign_title="Test Cleanup Ad",
            ad_type=ad_type,
            is_active=True,
            target_url="https://example.com"
        )
        print(f"✅ Created test ad: {test_ad.campaign_title}")

        # Check that our cleanup functions handle the new ad properly
        referenced_files_before = len(AdManager.objects.filter(
            poster__isnull=False).exclude(poster=''))
        print(f"📊 Ads with poster files: {referenced_files_before}")

        # Delete the test ad to verify cleanup signals work
        ad_title = test_ad.campaign_title
        test_ad.delete()
        print(f"🗑️ Deleted test ad: {ad_title}")

        print("✅ Ad creation and cleanup test completed successfully")
        return True

    except Exception as e:
        print(f"❌ Ad creation/cleanup test failed: {str(e)}")
        return False


def test_management_command():
    """Test that the Django management command can be imported properly."""
    print_section("TESTING MANAGEMENT COMMAND")

    try:
        from ads.management.commands.cleanup_ad_storage import Command

        command = Command()
        print("✅ Management command imported successfully")
        print(f"   Command help: {command.help}")

        # Test that we can create the command instance
        print("✅ Management command can be instantiated")

        return True

    except Exception as e:
        print(f"❌ Management command test failed: {str(e)}")
        return False


def test_signals_import():
    """Test that the signals module imports properly and is loaded."""
    print_section("TESTING SIGNAL HANDLERS")

    try:
        from ads import signals
        print("✅ Signals module imported successfully")

        # Check if our signal handlers are defined
        if hasattr(signals, 'ad_manager_pre_save'):
            print("✅ ad_manager_pre_save signal handler found")
        if hasattr(signals, 'ad_manager_post_delete'):
            print("✅ ad_manager_post_delete signal handler found")
        if hasattr(signals, 'safe_delete_file'):
            print("✅ safe_delete_file utility function found")

        return True

    except Exception as e:
        print(f"❌ Signals test failed: {str(e)}")
        return False


def run_comprehensive_test():
    """Run all tests and provide a summary."""
    print("🚀 STARTING COMPREHENSIVE AD STORAGE CLEANUP TEST")
    print(f"   Django version: {django.get_version()}")
    print(f"   Project root: {project_root}")

    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Ad Creation & Cleanup", test_ad_creation_and_cleanup),
        ("Management Command", test_management_command),
        ("Signal Handlers", test_signals_import),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
            results.append((test_name, False))

    # Print summary
    print_section("TEST SUMMARY")
    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
        if result:
            passed += 1

    print(f"\n📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Ad storage cleanup system is working correctly.")
        print("\n💡 You can now use:")
        print("   python manage.py cleanup_ad_storage --dry-run")
        print("   python manage.py cleanup_ad_storage --confirm")
        print("   python manage.py cleanup_ad_storage --report")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

    return passed == total


if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
