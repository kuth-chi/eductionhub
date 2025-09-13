"""
Storage cleanup utilities for the ads app.

This module provides functions to clean up orphaned image files
and manage storage efficiently for ad poster images.
"""

import os
from pathlib import Path
from typing import List, Set, Tuple

from django.conf import settings
from django.core.files.storage import default_storage

from ads.models import AdManager


def get_ads_poster_directory():
    """Get the directory path where ad posters are stored."""
    return 'uploads/admanager/posters/'


def scan_storage_files() -> List[str]:
    """
    Scan the storage directory and return a list of all poster files.

    Returns:
        List[str]: List of file paths relative to media root
    """
    poster_dir = get_ads_poster_directory()

    try:
        if not default_storage.exists(poster_dir):
            print(f"📁 Poster directory doesn't exist: {poster_dir}")
            return []

        # Get all files in the poster directory
        _, files = default_storage.listdir(poster_dir)
        file_paths = [os.path.join(poster_dir, f) for f in files]

        print(f"📁 Found {len(file_paths)} files in {poster_dir}")
        return file_paths

    except Exception as e:
        print(f"❌ Error scanning storage files: {str(e)}")
        return []


def get_referenced_poster_files() -> Set[str]:
    """
    Get a set of all poster files that are currently referenced by AdManager instances.

    Returns:
        Set[str]: Set of file paths that are still being used
    """
    referenced_files = set()

    try:
        # Get all ads that have poster files
        ads_with_posters = AdManager.objects.filter(
            poster__isnull=False).exclude(poster='')

        for ad in ads_with_posters:
            if ad.poster and ad.poster.name:
                referenced_files.add(ad.poster.name)

        print(f"📊 Found {len(referenced_files)} poster files still in use")
        return referenced_files

    except Exception as e:
        print(f"❌ Error getting referenced files: {str(e)}")
        return set()


def find_orphaned_files() -> Tuple[List[str], int]:
    """
    Find poster files that exist in storage but are not referenced by any AdManager.

    Returns:
        Tuple[List[str], int]: List of orphaned file paths and count
    """
    try:
        storage_files = scan_storage_files()
        referenced_files = get_referenced_poster_files()

        # Find files in storage that are not referenced in the database
        orphaned_files = []
        for file_path in storage_files:
            if file_path not in referenced_files:
                orphaned_files.append(file_path)

        print(f"🔍 Analysis complete:")
        print(f"   📁 Storage files: {len(storage_files)}")
        print(f"   🔗 Referenced files: {len(referenced_files)}")
        print(f"   🗑️  Orphaned files: {len(orphaned_files)}")

        return orphaned_files, len(orphaned_files)

    except Exception as e:
        print(f"❌ Error finding orphaned files: {str(e)}")
        return [], 0


def cleanup_orphaned_files(dry_run: bool = True) -> Tuple[List[str], List[str]]:
    """
    Clean up orphaned poster files from storage.

    Args:
        dry_run (bool): If True, only report what would be deleted without actually deleting

    Returns:
        Tuple[List[str], List[str]]: (successfully_deleted, failed_to_delete)
    """
    orphaned_files, count = find_orphaned_files()

    if count == 0:
        print("✅ No orphaned files found. Storage is clean!")
        return [], []

    if dry_run:
        print(f"🔍 DRY RUN: Would delete {count} orphaned files:")
        for file_path in orphaned_files:
            print(f"   • {file_path}")
        print("\n💡 Run with dry_run=False to actually delete these files")
        return [], []

    successfully_deleted = []
    failed_to_delete = []

    print(f"🗑️  Cleaning up {count} orphaned files...")

    for file_path in orphaned_files:
        try:
            if default_storage.exists(file_path):
                default_storage.delete(file_path)
                successfully_deleted.append(file_path)
                print(f"   ✅ Deleted: {file_path}")
            else:
                print(f"   ℹ️  Already gone: {file_path}")
                successfully_deleted.append(file_path)
        except Exception as e:
            failed_to_delete.append(file_path)
            print(f"   ❌ Failed to delete {file_path}: {str(e)}")

    print(f"\n📊 Cleanup Summary:")
    print(f"   ✅ Successfully deleted: {len(successfully_deleted)}")
    print(f"   ❌ Failed to delete: {len(failed_to_delete)}")

    return successfully_deleted, failed_to_delete


def calculate_storage_size() -> dict:
    """
    Calculate the total size of ad poster files in storage.

    Returns:
        dict: Storage statistics including total size and file counts
    """
    try:
        poster_files = scan_storage_files()
        total_size = 0
        file_sizes = []

        for file_path in poster_files:
            try:
                if default_storage.exists(file_path):
                    size = default_storage.size(file_path)
                    total_size += size
                    file_sizes.append(size)
            except Exception as e:
                print(f"⚠️  Could not get size for {file_path}: {str(e)}")

        # Convert to human-readable format
        def format_size(bytes_size):
            for unit in ['B', 'KB', 'MB', 'GB']:
                if bytes_size < 1024.0:
                    return f"{bytes_size:.1f} {unit}"
                bytes_size /= 1024.0
            return f"{bytes_size:.1f} TB"

        stats = {
            'total_files': len(poster_files),
            'total_size_bytes': total_size,
            'total_size_formatted': format_size(total_size),
            'average_size_bytes': total_size // len(poster_files) if poster_files else 0,
            'largest_file_bytes': max(file_sizes) if file_sizes else 0,
            'smallest_file_bytes': min(file_sizes) if file_sizes else 0,
        }

        print(f"💾 Storage Statistics for Ad Posters:")
        print(f"   📁 Total files: {stats['total_files']}")
        print(f"   📊 Total size: {stats['total_size_formatted']}")
        if stats['total_files'] > 0:
            print(
                f"   📈 Average size: {format_size(stats['average_size_bytes'])}")
            print(
                f"   📊 Largest file: {format_size(stats['largest_file_bytes'])}")
            print(
                f"   📊 Smallest file: {format_size(stats['smallest_file_bytes'])}")

        return stats

    except Exception as e:
        print(f"❌ Error calculating storage size: {str(e)}")
        return {
            'total_files': 0,
            'total_size_bytes': 0,
            'total_size_formatted': '0 B',
            'average_size_bytes': 0,
            'largest_file_bytes': 0,
            'smallest_file_bytes': 0,
        }


def validate_database_file_integrity() -> Tuple[List[str], List[str]]:
    """
    Check if all poster files referenced in the database actually exist in storage.

    Returns:
        Tuple[List[str], List[str]]: (existing_files, missing_files)
    """
    try:
        referenced_files = get_referenced_poster_files()
        existing_files = []
        missing_files = []

        print(f"🔍 Validating {len(referenced_files)} database references...")

        for file_path in referenced_files:
            if default_storage.exists(file_path):
                existing_files.append(file_path)
            else:
                missing_files.append(file_path)
                print(f"   ❌ Missing file: {file_path}")

        print(f"\n📊 Database Integrity Check:")
        print(f"   ✅ Files exist: {len(existing_files)}")
        print(f"   ❌ Files missing: {len(missing_files)}")

        if missing_files:
            print("\n⚠️  Warning: Some ads reference files that don't exist in storage!")
            print("   Consider updating these ads to remove broken file references.")

        return existing_files, missing_files

    except Exception as e:
        print(f"❌ Error validating database integrity: {str(e)}")
        return [], []


def get_cleanup_report() -> dict:
    """
    Generate a comprehensive cleanup report.

    Returns:
        dict: Complete report on storage status and cleanup recommendations
    """
    print("📋 Generating Comprehensive Storage Cleanup Report...")
    print("=" * 60)

    # Storage statistics
    storage_stats = calculate_storage_size()

    # Orphaned files analysis
    orphaned_files, orphaned_count = find_orphaned_files()

    # Database integrity check
    existing_files, missing_files = validate_database_file_integrity()

    report = {
        'timestamp': str(Path(__file__).stat().st_mtime),
        'storage_stats': storage_stats,
        'orphaned_files': {
            'count': orphaned_count,
            'files': orphaned_files
        },
        'integrity_check': {
            'existing_count': len(existing_files),
            'missing_count': len(missing_files),
            'missing_files': missing_files
        },
        'recommendations': []
    }

    # Generate recommendations
    if orphaned_count > 0:
        report['recommendations'].append(
            f"Clean up {orphaned_count} orphaned files to free storage space")

    if len(missing_files) > 0:
        report['recommendations'].append(
            f"Fix {len(missing_files)} database references to missing files")

    if storage_stats['total_size_bytes'] > 100 * 1024 * 1024:  # > 100MB
        report['recommendations'].append(
            "Consider implementing image compression for large poster files")

    if not report['recommendations']:
        report['recommendations'].append(
            "Storage is well-maintained, no action needed")

    print("\n📋 Cleanup Report Summary:")
    for recommendation in report['recommendations']:
        print(f"   • {recommendation}")

    return report
