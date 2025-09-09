# Ads Manager API Documentation

This document provides an overview of the Ads Manager API endpoints that have been implemented.

## Base URL
All endpoints are prefixed with `/api/v1/`

## Authentication
Most endpoints require authentication. Use JWT tokens for API access.

## Endpoints Overview

### Ad Types (`/api/v1/ad-types/`)
Manage different types of advertisements (image, video, HTML, etc.)

- **GET** `/api/v1/ad-types/` - List all ad types
- **POST** `/api/v1/ad-types/` - Create new ad type
- **GET** `/api/v1/ad-types/{id}/` - Get specific ad type
- **PUT** `/api/v1/ad-types/{id}/` - Update ad type
- **DELETE** `/api/v1/ad-types/{id}/` - Delete ad type

**Example Response:**
```json
{
  "id": 1,
  "name": "Banner Image",
  "description": "Standard banner advertisement with image"
}
```

### Ad Spaces (`/api/v1/ad-spaces/`)
Manage advertising spaces where ads can be placed

- **GET** `/api/v1/ad-spaces/` - List all ad spaces
- **POST** `/api/v1/ad-spaces/` - Create new ad space
- **GET** `/api/v1/ad-spaces/{id}/` - Get specific ad space
- **PUT** `/api/v1/ad-spaces/{id}/` - Update ad space
- **DELETE** `/api/v1/ad-spaces/{id}/` - Delete ad space
- **GET** `/api/v1/ad-spaces/{id}/analytics/` - Get analytics for ad space

**Example Response:**
```json
{
  "id": 1,
  "name": "Homepage Banner",
  "slug": "homepage-banner",
  "placement_count": 3
}
```

### Ad Campaigns (`/api/v1/ad-campaigns/`)
Manage advertising campaigns

- **GET** `/api/v1/ad-campaigns/` - List all campaigns
- **POST** `/api/v1/ad-campaigns/` - Create new campaign
- **GET** `/api/v1/ad-campaigns/{uuid}/` - Get specific campaign
- **PUT** `/api/v1/ad-campaigns/{uuid}/` - Update campaign
- **DELETE** `/api/v1/ad-campaigns/{uuid}/` - Delete campaign
- **POST** `/api/v1/ad-campaigns/{uuid}/activate/` - Activate campaign
- **POST** `/api/v1/ad-campaigns/{uuid}/deactivate/` - Deactivate campaign
- **GET** `/api/v1/ad-campaigns/{uuid}/analytics/` - Get campaign analytics
- **GET** `/api/v1/ad-campaigns/dashboard_stats/` - Get dashboard statistics

**Example Response (List):**
```json
{
  "results": [
    {
      "uuid": "123e4567-e89b-12d3-a456-426614174000",
      "campaign_title": "Summer Sale 2024",
      "ad_type_name": "Banner Image",
      "start_datetime": "2024-06-01",
      "end_datetime": "2024-08-31",
      "is_active": true,
      "is_currently_active": true,
      "placement_count": 2,
      "days_remaining": 45,
      "create_datetime": "2024-05-15T10:30:00Z"
    }
  ]
}
```

**Example Response (Detail):**
```json
{
  "uuid": "123e4567-e89b-12d3-a456-426614174000",
  "campaign_title": "Summer Sale 2024",
  "ad_type": 1,
  "ad_type_name": "Banner Image",
  "tags": ["sale", "summer", "discount"],
  "start_datetime": "2024-06-01",
  "end_datetime": "2024-08-31",
  "is_active": true,
  "is_currently_active": true,
  "active_ad_period": null,
  "limited_overdue": 7,
  "poster": "/media/uploads/admanager/posters/summer-sale-uuid.jpg",
  "placements": [
    {
      "id": 1,
      "ad_space_name": "Homepage Banner",
      "position": 1,
      "is_primary": true
    }
  ],
  "impression_count": 15420,
  "click_count": 342,
  "click_through_rate": 2.22,
  "create_datetime": "2024-05-15T10:30:00Z",
  "update_datetime": "2024-06-01T08:00:00Z"
}
```

### Ad Placements (`/api/v1/ad-placements/`)
Manage where ads are placed within ad spaces

- **GET** `/api/v1/ad-placements/` - List all placements
- **POST** `/api/v1/ad-placements/` - Create new placement
- **GET** `/api/v1/ad-placements/{id}/` - Get specific placement
- **PUT** `/api/v1/ad-placements/{id}/` - Update placement
- **DELETE** `/api/v1/ad-placements/{id}/` - Delete placement
- **POST** `/api/v1/ad-placements/reorder/` - Reorder placements

**Example Response:**
```json
{
  "id": 1,
  "ad": "123e4567-e89b-12d3-a456-426614174000",
  "ad_space": 1,
  "ad_title": "Summer Sale 2024",
  "ad_space_name": "Homepage Banner",
  "position": 1,
  "is_primary": true
}
```

### Ad Impressions (`/api/v1/ad-impressions/`)
Track when ads are shown to users

- **GET** `/api/v1/ad-impressions/` - List impressions (last 90 days by default)
- **POST** `/api/v1/ad-impressions/` - Record new impression
- **GET** `/api/v1/ad-impressions/{id}/` - Get specific impression

**Query Parameters:**
- `days` - Number of days to include (default: 90)
- `ad` - Filter by ad UUID
- `user_id` - Filter by user ID

### Ad Clicks (`/api/v1/ad-clicks/`)
Track when users click on ads

- **GET** `/api/v1/ad-clicks/` - List clicks (last 90 days by default)
- **POST** `/api/v1/ad-clicks/` - Record new click
- **GET** `/api/v1/ad-clicks/{id}/` - Get specific click

### User Profiles (`/api/v1/ads-user-profiles/`)
Manage user interest profiles for ad targeting

- **GET** `/api/v1/ads-user-profiles/` - List user profiles
- **POST** `/api/v1/ads-user-profiles/` - Create user profile
- **GET** `/api/v1/ads-user-profiles/{id}/` - Get specific profile
- **PUT** `/api/v1/ads-user-profiles/{id}/` - Update profile

### User Behavior (`/api/v1/user-behavior/`)
Track user behavior for ad targeting

- **GET** `/api/v1/user-behavior/` - List behavior data (last 30 days by default)
- **POST** `/api/v1/user-behavior/` - Record behavior

## Filtering and Search

Most endpoints support filtering, searching, and ordering:

### Common Query Parameters:
- `search` - Full-text search across relevant fields
- `ordering` - Order results by field (prefix with `-` for descending)
- `page` - Page number for pagination
- `page_size` - Number of results per page

### Ad Campaigns Specific Filters:
- `campaign_title` - Filter by campaign title (contains)
- `ad_type` - Filter by ad type ID
- `is_active` - Filter by active status (true/false)
- `is_currently_active` - Filter by current active status
- `start_date_after` - Filter campaigns starting after date
- `start_date_before` - Filter campaigns starting before date
- `end_date_after` - Filter campaigns ending after date
- `end_date_before` - Filter campaigns ending before date
- `tags` - Filter by tags (contains)

**Example:**
```
GET /api/v1/ad-campaigns/?is_currently_active=true&search=summer&ordering=-create_datetime
```

## Analytics Endpoints

### Campaign Analytics
Get detailed analytics for a specific campaign:
```
GET /api/v1/ad-campaigns/{uuid}/analytics/?days=30
```

**Response:**
```json
{
  "ad_uuid": "123e4567-e89b-12d3-a456-426614174000",
  "campaign_title": "Summer Sale 2024",
  "total_impressions": 15420,
  "total_clicks": 342,
  "click_through_rate": 2.22,
  "unique_users": 8934,
  "avg_daily_impressions": 514.0,
  "date_range": "2024-07-01 to 2024-07-30"
}
```

### Dashboard Statistics
Get overall statistics for the ads dashboard:
```
GET /api/v1/ad-campaigns/dashboard_stats/
```

**Response:**
```json
{
  "total_ads": 25,
  "active_ads": 12,
  "expiring_soon": 3,
  "total_impressions_30d": 125430,
  "total_clicks_30d": 2834,
  "average_ctr_30d": 2.26
}
```

### Ad Space Analytics
Get analytics for a specific ad space:
```
GET /api/v1/ad-spaces/{id}/analytics/
```

**Response:**
```json
{
  "space_name": "Homepage Banner",
  "total_ads": 5,
  "active_ads": 3,
  "total_impressions": 45230,
  "total_clicks": 1256,
  "average_ctr": 2.78
}
```

## Error Responses

The API returns standard HTTP status codes:

- `200` - Success
- `201` - Created
- `400` - Bad Request (validation errors)
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

**Error Response Format:**
```json
{
  "error": "Validation failed",
  "details": {
    "end_datetime": ["End date must be after start date."]
  }
}
```

## Usage Examples

### Create a New Ad Campaign
```bash
curl -X POST /api/v1/ad-campaigns/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_title": "Winter Sale 2024",
    "ad_type": 1,
    "tags": ["sale", "winter", "discount"],
    "start_datetime": "2024-12-01",
    "end_datetime": "2024-12-31",
    "is_active": true,
    "limited_overdue": 7
  }'
```

### Place an Ad in an Ad Space
```bash
curl -X POST /api/v1/ad-placements/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ad": "123e4567-e89b-12d3-a456-426614174000",
    "ad_space": 1,
    "position": 1,
    "is_primary": true
  }'
```

### Record an Ad Impression
```bash
curl -X POST /api/v1/ad-impressions/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ad": "123e4567-e89b-12d3-a456-426614174000",
    "user_id": "user123",
    "session_id": "session456",
    "user_agent": "Mozilla/5.0...",
    "ip_address": "192.168.1.1"
  }'
```

This API provides comprehensive functionality for managing advertisements, tracking performance, and analyzing user engagement.
