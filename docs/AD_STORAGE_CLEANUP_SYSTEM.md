# Ad Storage Management System Documentation

## Overview

The EducationHub backend now includes a comprehensive file storage management system for ad poster images. This system automatically handles cleanup when logos are changed or deleted, preventing storage bloat and ensuring efficient resource management.

## 🎯 Problem Solved

**Before**: When ad logos were updated or ads were deleted, the old image files remained in storage, wasting disk space and potentially causing confusion.

**After**: Automatic cleanup ensures old files are immediately deleted when no longer needed, with tools for maintenance and monitoring.

## 🏗️ Architecture Components

### 1. Automatic Cleanup Signals (`ads/signals.py`)

**Purpose**: Handle immediate cleanup when ads are modified or deleted

**Key Functions**:
- `safe_delete_file()`: Safely delete files with error handling
- `ad_manager_pre_save()`: Cleanup old poster when ad is updated
- `ad_manager_post_delete()`: Cleanup poster when ad is deleted

**How it works**:
```python
# When an ad poster is changed
old_ad = AdManager.objects.get(pk=1)  # Has poster: old_logo.jpg
old_ad.poster = new_image_file        # Upload new_logo.jpg
old_ad.save()                         # old_logo.jpg automatically deleted
```

### 2. Storage Utilities (`ads/utils/storage_cleanup.py`)

**Purpose**: Comprehensive storage analysis and cleanup tools

**Key Functions**:
- `find_orphaned_files()`: Identify files not referenced in database
- `cleanup_orphaned_files()`: Remove orphaned files (with dry-run option)
- `validate_database_file_integrity()`: Check for missing file references
- `calculate_storage_size()`: Storage usage statistics
- `get_cleanup_report()`: Comprehensive analysis report

### 3. Management Command (`ads/management/commands/cleanup_ad_storage.py`)

**Purpose**: Command-line interface for storage maintenance

**Available Commands**:
```bash
# Preview cleanup (safe to run anytime)
python manage.py cleanup_ad_storage --dry-run

# Actually delete orphaned files
python manage.py cleanup_ad_storage --confirm

# Generate comprehensive report
python manage.py cleanup_ad_storage --report

# Check database integrity
python manage.py cleanup_ad_storage --integrity-check

# Show storage statistics only
python manage.py cleanup_ad_storage --stats
```

## 🔄 Workflow Examples

### Logo Update Scenario
```python
# Django Admin or API
ad = AdManager.objects.get(uuid='some-uuid')
ad.poster = new_uploaded_image  # Triggers automatic cleanup
ad.save()                       # Old image deleted, new image saved
```

### Ad Deletion Scenario
```python
# Django Admin or API
ad = AdManager.objects.get(uuid='some-uuid')
ad.delete()  # Both database record AND poster file deleted
```

### Maintenance Tasks
```bash
# Weekly cleanup of orphaned files
python manage.py cleanup_ad_storage --dry-run    # Check what would be deleted
python manage.py cleanup_ad_storage --confirm    # Actually clean up

# Monthly storage report
python manage.py cleanup_ad_storage --report > storage_report.txt
```

## 🛡️ Safety Features

1. **Dry Run Mode**: Preview changes without making them
2. **Error Handling**: Graceful failure handling with detailed logging
3. **File Existence Checks**: Verify files exist before attempting deletion
4. **Database Integrity**: Ensure file references match actual files
5. **Detailed Logging**: Track all cleanup operations with timestamps

## 📊 Storage Analysis Features

The system provides comprehensive storage analysis:

- **File Count**: Total number of poster files
- **Storage Size**: Total disk space used by posters
- **Orphaned Files**: Files not referenced by any ad
- **Missing References**: Database entries pointing to non-existent files
- **Cleanup Recommendations**: Automated suggestions for optimization

## 🔧 Configuration

The system uses Django's default file storage configuration:

```python
# settings.py (already configured)
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
```

Poster files are stored in: `media/uploads/admanager/posters/`

## 🚀 Production Recommendations

### 1. Automated Cleanup
Set up a weekly cron job:
```bash
# Add to crontab
0 2 * * 0 cd /path/to/project && python manage.py cleanup_ad_storage --confirm
```

### 2. Monitoring
Monthly storage reports:
```bash
# Add to crontab  
0 9 1 * * cd /path/to/project && python manage.py cleanup_ad_storage --report | mail -s "Storage Report" admin@example.com
```

### 3. Backup Strategy
Before running cleanup in production:
```bash
# Backup media directory
tar -czf media_backup_$(date +%Y%m%d).tar.gz media/
```

## 🧪 Testing

Test the system by:

1. **Create Test Ad**: Upload a logo through Django admin
2. **Update Logo**: Change the poster image - verify old file is deleted
3. **Delete Ad**: Remove the ad - verify poster file is also deleted
4. **Run Cleanup**: Use `--dry-run` to see orphaned files
5. **Generate Report**: Check storage statistics and recommendations

## 🔍 Monitoring & Troubleshooting

### Check Storage Status
```bash
python manage.py cleanup_ad_storage --stats
```

### Find Problems
```bash
python manage.py cleanup_ad_storage --integrity-check
```

### Debug Issues
- Check Django logs for cleanup operation messages
- Verify file permissions on media directory
- Ensure storage backend is properly configured

## ⚡ Performance Considerations

- **Immediate Cleanup**: Files deleted immediately on save/delete (no batch processing needed)
- **Efficient Queries**: Uses database queries optimized for large datasets
- **Memory Usage**: Processes files in chunks to avoid memory issues
- **Error Recovery**: Continues processing even if individual files fail

## 📚 File Structure

```
ads/
├── models.py                 # AdManager with poster ImageField
├── signals.py               # Automatic cleanup signal handlers
├── utils/
│   └── storage_cleanup.py   # Storage management utilities  
└── management/
    └── commands/
        └── cleanup_ad_storage.py  # Management command
```

## 🎉 Benefits

1. **Zero-Maintenance**: Files automatically cleaned up without manual intervention
2. **Storage Efficiency**: No wasted disk space from orphaned files
3. **Data Integrity**: Database and file system stay synchronized
4. **Monitoring Tools**: Comprehensive reporting and analysis
5. **Production Ready**: Safe operations with dry-run modes and error handling
6. **Scalable**: Efficient processing for large numbers of files

## 🔄 Migration Notes

This system is **backwards compatible** - it doesn't affect existing ads or require data migration. It simply adds cleanup functionality for future operations.

---

**Implementation Complete** ✅  
The ad storage cleanup system is now active and will automatically manage logo files when ads are updated or deleted.