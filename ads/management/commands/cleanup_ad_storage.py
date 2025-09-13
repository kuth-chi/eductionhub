"""
Django management command to clean up orphaned ad poster files.

Usage examples:
    python manage.py cleanup_ad_storage --dry-run          # See what would be deleted
    python manage.py cleanup_ad_storage --confirm          # Actually delete orphaned files
    python manage.py cleanup_ad_storage --report           # Generate detailed report
    python manage.py cleanup_ad_storage --integrity-check  # Check database file integrity
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from ads.utils.storage_cleanup import (calculate_storage_size,
                                       cleanup_orphaned_files,
                                       find_orphaned_files, get_cleanup_report,
                                       validate_database_file_integrity)


class Command(BaseCommand):
    help = 'Clean up orphaned ad poster files and manage storage efficiently'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting files',
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Actually delete orphaned files (requires explicit confirmation)',
        )
        parser.add_argument(
            '--report',
            action='store_true',
            help='Generate a comprehensive storage cleanup report',
        )
        parser.add_argument(
            '--integrity-check',
            action='store_true',
            help='Check if database references point to existing files',
        )
        parser.add_argument(
            '--stats',
            action='store_true',
            help='Display storage statistics only',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🧹 Ad Storage Cleanup Tool - {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}'
            )
        )
        self.stdout.write('=' * 70)

        try:
            if options['stats']:
                self.handle_stats()
            elif options['integrity_check']:
                self.handle_integrity_check()
            elif options['report']:
                self.handle_report()
            elif options['confirm']:
                self.handle_cleanup(dry_run=False)
            elif options['dry_run']:
                self.handle_cleanup(dry_run=True)
            else:
                self.show_usage()

        except Exception as e:
            raise CommandError(f'Command failed: {str(e)}')

    def show_usage(self):
        """Show usage instructions when no specific action is provided."""
        self.stdout.write(
            self.style.WARNING(
                '\n📖 No action specified. Choose one of the following options:\n')
        )

        usage_options = [
            ('--dry-run', 'Preview what orphaned files would be deleted'),
            ('--confirm', 'Actually delete orphaned files (DESTRUCTIVE)'),
            ('--report', 'Generate comprehensive storage report'),
            ('--integrity-check', 'Check database file integrity'),
            ('--stats', 'Display storage statistics'),
        ]

        for option, description in usage_options:
            self.stdout.write(
                f'   {self.style.SUCCESS(option.ljust(20))} {description}')

        self.stdout.write(
            self.style.HTTP_INFO(
                '\n💡 Tip: Start with --dry-run to see what would be cleaned up')
        )

    def handle_stats(self):
        """Handle storage statistics display."""
        self.stdout.write(self.style.HTTP_REDIRECT(
            '\n📊 Calculating Storage Statistics...\n'))

        stats = calculate_storage_size()

        self.stdout.write(f"📁 Total Files: {stats['total_files']}")
        self.stdout.write(f"💾 Total Size: {stats['total_size_formatted']}")

        if stats['total_files'] > 0:
            self.stdout.write(
                f"📈 Average Size: {stats['total_size_formatted']}")

        if stats['total_size_bytes'] > 50 * 1024 * 1024:  # > 50MB
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  Large storage usage detected - consider cleanup')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('✅ Storage usage within reasonable limits')
            )

    def handle_integrity_check(self):
        """Handle database file integrity check."""
        self.stdout.write(self.style.HTTP_REDIRECT(
            '\n🔍 Checking Database File Integrity...\n'))

        existing_files, missing_files = validate_database_file_integrity()

        if missing_files:
            self.stdout.write(
                self.style.ERROR(
                    f'❌ Found {len(missing_files)} missing files:')
            )
            for file_path in missing_files:
                self.stdout.write(f'   • {file_path}')

            self.stdout.write(
                self.style.WARNING(
                    '\n⚠️  Consider updating ads with missing files or restoring the files'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    '✅ All database references point to existing files')
            )

    def handle_report(self):
        """Handle comprehensive report generation."""
        self.stdout.write(self.style.HTTP_REDIRECT(
            '\n📋 Generating Comprehensive Report...\n'))

        report = get_cleanup_report()

        self.stdout.write(self.style.SUCCESS('\n📋 Storage Cleanup Report:'))
        self.stdout.write('-' * 40)

        # Storage stats
        stats = report['storage_stats']
        self.stdout.write(f"📁 Total Files: {stats['total_files']}")
        self.stdout.write(f"💾 Storage Used: {stats['total_size_formatted']}")

        # Orphaned files
        orphaned = report['orphaned_files']
        if orphaned['count'] > 0:
            self.stdout.write(self.style.WARNING(
                f"🗑️  Orphaned Files: {orphaned['count']}"))
        else:
            self.stdout.write(self.style.SUCCESS("🗑️  Orphaned Files: 0"))

        # Integrity issues
        integrity = report['integrity_check']
        if integrity['missing_count'] > 0:
            self.stdout.write(self.style.ERROR(
                f"❌ Missing Files: {integrity['missing_count']}"))
        else:
            self.stdout.write(self.style.SUCCESS("❌ Missing Files: 0"))

        # Recommendations
        self.stdout.write(self.style.HTTP_INFO('\n💡 Recommendations:'))
        for recommendation in report['recommendations']:
            self.stdout.write(f'   • {recommendation}')

    def handle_cleanup(self, dry_run=True):
        """Handle file cleanup operation."""
        if dry_run:
            self.stdout.write(self.style.HTTP_REDIRECT(
                '\n🔍 DRY RUN - Preview Mode\n'))
        else:
            self.stdout.write(self.style.WARNING(
                '\n🗑️  CLEANUP MODE - Files will be deleted!\n'))

        # First, find orphaned files
        orphaned_files, count = find_orphaned_files()

        if count == 0:
            self.stdout.write(self.style.SUCCESS(
                '✅ No orphaned files found. Storage is clean!'))
            return

        if dry_run:
            self.stdout.write(
                self.style.HTTP_INFO(
                    f'Found {count} orphaned files that would be deleted:')
            )
            for file_path in orphaned_files:
                self.stdout.write(f'   • {file_path}')

            self.stdout.write(
                self.style.WARNING(
                    f'\n💡 Run with --confirm to actually delete these {count} files'
                )
            )
        else:
            # Confirm deletion
            self.stdout.write(
                self.style.ERROR(
                    f'⚠️  About to delete {count} orphaned files!')
            )

            # Actually perform cleanup
            self.stdout.write(self.style.WARNING('Proceeding with cleanup...'))

            successfully_deleted, failed_to_delete = cleanup_orphaned_files(
                dry_run=False)

            if successfully_deleted:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Successfully deleted {len(successfully_deleted)} files')
                )

            if failed_to_delete:
                self.stdout.write(
                    self.style.ERROR(
                        f'❌ Failed to delete {len(failed_to_delete)} files:')
                )
                for file_path in failed_to_delete:
                    self.stdout.write(f'   • {file_path}')

            if not failed_to_delete and successfully_deleted:
                self.stdout.write(self.style.SUCCESS(
                    '\n🎉 Cleanup completed successfully!'))

    def handle_no_args(self, **options):
        """Show help when no arguments provided."""
        self.show_usage()
