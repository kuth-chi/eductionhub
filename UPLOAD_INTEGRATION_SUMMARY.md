# School Upload Integration Summary

## Current Implementation Status: ✅ FULLY WORKING

The SchoolViewSet is successfully integrated with the SchoolEditHero component to handle logo and cover image uploads.

## Implementation Details

### Backend (Django)

1. **SchoolViewSet** (`api/views/schools/schools_api.py`)
   - ✅ `parser_classes = (MultiPartParser, FormParser)`
   - ✅ Handles PATCH requests for file uploads
   - ✅ Proper error handling with Pylint warnings resolved

2. **SchoolSerializer** (`api/serializers/schools/base.py`)
   - ✅ `logo = serializers.ImageField(required=False, allow_null=True, allow_empty_file=True)`
   - ✅ `cover_image = serializers.ImageField(required=False, allow_null=True, allow_empty_file=True)`
   - ✅ Custom `update()` method handles both file uploads and URL strings
   - ✅ Proper `to_representation()` for URL handling

3. **School Model** (`schools/models/school.py`)
   - ✅ `logo = models.ImageField(upload_to=school_logo_upload_path, null=True, blank=True)`
   - ✅ `cover_image = models.ImageField(upload_to=school_cover_image_upload_path, null=True, blank=True)`

### Frontend (Next.js)

1. **SchoolEditHero Component** (`modules/schools/ui/components/school-edit-hero.tsx`)
   - ✅ File input with proper file type validation
   - ✅ FormData creation for multipart uploads
   - ✅ PATCH requests to `/api/v1/schools/{uuid}/`
   - ✅ Real-time preview and error handling
   - ✅ Authentication integration via `authFetch`

2. **SchoolService** (`modules/schools/services/school-service.ts`)
   - ✅ `partialUpdate()` method for PATCH requests
   - ✅ Proper error handling and logging

## Upload Flow

```
User selects file → FormData creation → PATCH /api/v1/schools/{uuid}/ → 
SchoolViewSet.partial_update() → SchoolSerializer.update() → 
File saved to filesystem → Database updated → Response with new URLs → 
Component state updated → UI refreshed with new image
```

## API Endpoints

- **PATCH** `/api/v1/schools/{uuid}/` - Update school (including file uploads)
- **Content-Type**: `multipart/form-data` (automatically set by browser for FormData)
- **Fields**: `logo` (File), `cover_image` (File)

## File Validation

- **Logo**: PNG, JPG, GIF, WebP, SVG up to 5MB
- **Cover**: PNG, JPG, GIF, WebP, SVG up to 10MB
- **Error handling**: Invalid file types, size limits, network errors

## Authentication

- Uses `authFetch` with JWT tokens
- Authorization header to cookie conversion in proxy route
- Proper error handling for authentication failures

## Testing

The upload functionality has been tested and confirmed working:
- ✅ File selection and preview
- ✅ FormData upload to backend
- ✅ File processing and storage
- ✅ Database update with new URLs
- ✅ UI update with new images
- ✅ Error handling for various scenarios

## Recent Fixes Applied

1. **Pylint Warnings**: Added `# pylint: disable=no-member` for Django model managers
2. **Parser Classes**: Added `MultiPartParser` and `FormParser` to SchoolViewSet
3. **FormData Handling**: Enhanced proxy route to properly detect and handle multipart data
4. **Authentication**: Improved Authorization header to cookie conversion

## Status: Ready for Production ✅

The integration is complete and fully functional. Users can successfully upload and update school logos and cover images through the SchoolEditHero component.
