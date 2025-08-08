# Schools API Documentation

## Overview

The Schools API provides comprehensive endpoints for managing educational institutions. This API supports full CRUD operations for schools, including related data like educational levels, school types, and platform profiles.

**Base URL:** `http://localhost:8000/api/v1/`

## Authentication

- **Public Endpoints:** `GET` operations (list, retrieve) are publicly accessible
- **Protected Endpoints:** `POST`, `PUT`, `PATCH`, `DELETE` operations require authentication
- **Authentication Method:** JWT Token (Bearer token in Authorization header)

## Endpoints

### 1. List Schools

**GET** `/api/v1/schools/`

Retrieve a list of all schools with optional filtering and pagination.

#### Query Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `search` | string | Search schools by name, local_name, president, or founder | `?search=university` |
| `type` | integer | Filter by school type ID | `?type=1` |
| `create_date` | date | Filter by creation date | `?create_date=2024-01-01` |
| `ordering` | string | Sort results by field | `?ordering=name` |

#### Response Example

```json
[
  {
    "pk": 1,
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Royal University of Phnom Penh",
    "local_name": "សាកលវិទ្យាល័យភូមិន្ទភ្នំពេញ",
    "logo": "/media/uploads/schools/logos/rupp-logo.png",
    "cover_image": "/media/uploads/schools/cover/rupp-cover.jpg",
    "short_name": "RUPP",
    "code": "RUPP001",
    "description": "Leading public university in Cambodia",
    "founder": "Royal Government of Cambodia",
    "president": "Dr. Chet Chealy",
    "established": "1960-01-01",
    "street_address": "Russian Federation Blvd",
    "address_line_2": "Toul Kork",
    "box_number": "P.O. Box 1234",
    "postal_code": "12156",
    "country": 1,
    "state": 1,
    "city": 1,
    "village": null,
    "location": "Phnom Penh, Cambodia",
    "motto": "Excellence in Education",
    "tuition": "500.00",
    "endowment": "1000000.00",
    "created_date": "2024-01-15T10:30:00Z",
    "updated_date": "2024-01-15T10:30:00Z",
    "slug": "royal-university-phnom-penh",
    "is_active": true,
    "self_data": "RUPP_DATA",
    "type": [
      {
        "id": 1,
        "uuid": "550e8400-e29b-41d4-a716-446655440001",
        "type": "Public University",
        "description": "Government-funded higher education institution",
        "icon": "university",
        "created_date": "2024-01-01T00:00:00Z",
        "updated_date": "2024-01-01T00:00:00Z",
        "is_active": true
      }
    ],
    "educational_levels": [
      {
        "id": 1,
        "uuid": "550e8400-e29b-41d4-a716-446655440002",
        "level_name": "Bachelor's Degree",
        "badge": "BA",
        "color": "#1D4ED8",
        "description": "Undergraduate degree program",
        "order": 1,
        "parent_level": null,
        "slug": "bachelors-degree",
        "created_date": "2024-01-01T00:00:00Z",
        "updated_date": "2024-01-01T00:00:00Z",
        "is_active": true,
        "is_deleted": false
      }
    ],
    "platform_profiles": [
      {
        "id": 1,
        "uuid": "550e8400-e29b-41d4-a716-446655440003",
        "profile_url": "https://facebook.com/rupp",
        "username": "rupp_official",
        "platform": {
          "id": 1,
          "uuid": "550e8400-e29b-41d4-a716-446655440004",
          "name": "Facebook",
          "short_name": "FB",
          "url": "https://facebook.com",
          "icon": "facebook",
          "created_date": "2024-01-01T00:00:00Z",
          "updated_date": "2024-01-01T00:00:00Z",
          "is_active": true
        },
        "school": 1,
        "created_date": "2024-01-01T00:00:00Z",
        "updated_date": "2024-01-01T00:00:00Z",
        "is_active": true
      }
    ]
  }
]
```

### 2. Retrieve Single School

**GET** `/api/v1/schools/{uuid}/`

Retrieve detailed information about a specific school.

#### Path Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `uuid` | string | School's unique identifier | `550e8400-e29b-41d4-a716-446655440000` |

#### Response Example

```json
{
  "pk": 1,
  "uuid": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Royal University of Phnom Penh",
  "local_name": "សាកលវិទ្យាល័យភូមិន្ទភ្នំពេញ",
  "logo": "/media/uploads/schools/logos/rupp-logo.png",
  "cover_image": "/media/uploads/schools/cover/rupp-cover.jpg",
  "short_name": "RUPP",
  "code": "RUPP001",
  "description": "Leading public university in Cambodia",
  "founder": "Royal Government of Cambodia",
  "president": "Dr. Chet Chealy",
  "established": "1960-01-01",
  "street_address": "Russian Federation Blvd",
  "address_line_2": "Toul Kork",
  "box_number": "P.O. Box 1234",
  "postal_code": "12156",
  "country": 1,
  "state": 1,
  "city": 1,
  "village": null,
  "location": "Phnom Penh, Cambodia",
  "motto": "Excellence in Education",
  "tuition": "500.00",
  "endowment": "1000000.00",
  "created_date": "2024-01-15T10:30:00Z",
  "updated_date": "2024-01-15T10:30:00Z",
  "slug": "royal-university-phnom-penh",
  "is_active": true,
  "self_data": "RUPP_DATA",
  "type": [...],
  "educational_levels": [...],
  "platform_profiles": [...]
}
```

### 3. Create School

**POST** `/api/v1/schools/`

Create a new school (requires authentication).

#### Request Headers

```
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

#### Request Body

```json
{
  "name": "New University",
  "local_name": "សាកលវិទ្យាល័យថ្មី",
  "short_name": "NU",
  "code": "NU001",
  "description": "A new educational institution",
  "founder": "Ministry of Education",
  "president": "Dr. John Doe",
  "established": "2024-01-01",
  "street_address": "123 Education Street",
  "address_line_2": "Building A",
  "box_number": "P.O. Box 5678",
  "postal_code": "12345",
  "country": 1,
  "state": 1,
  "city": 1,
  "location": "Phnom Penh, Cambodia",
  "motto": "Learning for Life",
  "tuition": "800.00",
  "endowment": "500000.00",
  "is_active": true,
  "self_data": "NU_DATA",
  "type_ids": [1, 2],
  "educational_level_ids": [1, 2, 3]
}
```

#### Response

```json
{
  "pk": 2,
  "uuid": "550e8400-e29b-41d4-a716-446655440005",
  "name": "New University",
  "local_name": "សាកលវិទ្យាល័យថ្មី",
  "logo": null,
  "cover_image": null,
  "short_name": "NU",
  "code": "NU001",
  "description": "A new educational institution",
  "founder": "Ministry of Education",
  "president": "Dr. John Doe",
  "established": "2024-01-01",
  "street_address": "123 Education Street",
  "address_line_2": "Building A",
  "box_number": "P.O. Box 5678",
  "postal_code": "12345",
  "country": 1,
  "state": 1,
  "city": 1,
  "village": null,
  "location": "Phnom Penh, Cambodia",
  "motto": "Learning for Life",
  "tuition": "800.00",
  "endowment": "500000.00",
  "created_date": "2024-01-15T11:00:00Z",
  "updated_date": "2024-01-15T11:00:00Z",
  "slug": "new-university-abc123",
  "is_active": true,
  "self_data": "NU_DATA",
  "type": [...],
  "educational_levels": [...],
  "platform_profiles": []
}
```

### 4. Update School

**PUT** `/api/v1/schools/{uuid}/`

Update all fields of a school (requires authentication).

#### Request Headers

```
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

#### Request Body

```json
{
  "name": "Updated University Name",
  "description": "Updated description",
  "tuition": "900.00",
  "type_ids": [1],
  "educational_level_ids": [1, 2]
}
```

### 5. Partial Update School

**PATCH** `/api/v1/schools/{uuid}/`

Update specific fields of a school (requires authentication).

#### Request Headers

```
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

#### Request Body

```json
{
  "tuition": "950.00",
  "description": "Updated description only"
}
```

### 6. Delete School

**DELETE** `/api/v1/schools/{uuid}/`

Delete a school (requires authentication).

#### Request Headers

```
Authorization: Bearer <your_jwt_token>
```

#### Response

- **Success:** `204 No Content`
- **Not Found:** `404 Not Found`

### 7. School Analytics

**GET** `/api/v1/schools/{uuid}/analytics/`

Get analytics data for a specific school.

#### Response Example

```json
{
  "total_branches": 3,
  "total_degree_offerings": 15,
  "total_major_offerings": 25,
  "total_custom_buttons": 5,
  "total_platform_profiles": 8,
  "total_scholarships": 12,
  "total_college_associations": 7
}
```

## Data Models

### School Object

| Field | Type | Description | Required | Example |
|-------|------|-------------|----------|---------|
| `pk` | integer | Primary key | Auto | `1` |
| `uuid` | string | Unique identifier | Auto | `"550e8400-e29b-41d4-a716-446655440000"` |
| `name` | string | School name | Yes | `"Royal University of Phnom Penh"` |
| `local_name` | string | Local language name | No | `"សាកលវិទ្យាល័យភូមិន្ទភ្នំពេញ"` |
| `logo` | string | Logo image URL | No | `"/media/uploads/schools/logos/logo.png"` |
| `cover_image` | string | Cover image URL | No | `"/media/uploads/schools/cover/cover.jpg"` |
| `short_name` | string | Abbreviated name | No | `"RUPP"` |
| `code` | string | School code | No | `"RUPP001"` |
| `description` | string | School description | No | `"Leading public university"` |
| `founder` | string | School founder | No | `"Royal Government"` |
| `president` | string | Current president | No | `"Dr. Chet Chealy"` |
| `established` | date | Establishment date | No | `"1960-01-01"` |
| `street_address` | string | Street address | No | `"Russian Federation Blvd"` |
| `address_line_2` | string | Additional address | No | `"Toul Kork"` |
| `box_number` | string | P.O. Box number | No | `"P.O. Box 1234"` |
| `postal_code` | string | Postal code | No | `"12156"` |
| `country` | integer | Country ID | No | `1` |
| `state` | integer | State ID | No | `1` |
| `city` | integer | City ID | No | `1` |
| `village` | integer | Village ID | No | `null` |
| `location` | string | Legacy location field | No | `"Phnom Penh, Cambodia"` |
| `motto` | string | School motto | No | `"Excellence in Education"` |
| `tuition` | decimal | Annual tuition fee | No | `"500.00"` |
| `endowment` | decimal | Endowment amount | No | `"1000000.00"` |
| `created_date` | datetime | Creation timestamp | Auto | `"2024-01-15T10:30:00Z"` |
| `updated_date` | datetime | Last update timestamp | Auto | `"2024-01-15T10:30:00Z"` |
| `slug` | string | URL-friendly identifier | Auto | `"royal-university-phnom-penh"` |
| `is_active` | boolean | Active status | No | `true` |
| `self_data` | string | Custom data field | No | `"RUPP_DATA"` |
| `type` | array | School types | No | `[{...}]` |
| `educational_levels` | array | Educational levels | No | `[{...}]` |
| `platform_profiles` | array | Social media profiles | No | `[{...}]` |

### School Type Object

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | integer | Primary key | `1` |
| `uuid` | string | Unique identifier | `"550e8400-e29b-41d4-a716-446655440001"` |
| `type` | string | Type name | `"Public University"` |
| `description` | string | Type description | `"Government-funded institution"` |
| `icon` | string | Icon identifier | `"university"` |
| `created_date` | datetime | Creation timestamp | `"2024-01-01T00:00:00Z"` |
| `updated_date` | datetime | Last update timestamp | `"2024-01-01T00:00:00Z"` |
| `is_active` | boolean | Active status | `true` |

### Educational Level Object

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | integer | Primary key | `1` |
| `uuid` | string | Unique identifier | `"550e8400-e29b-41d4-a716-446655440002"` |
| `level_name` | string | Level name | `"Bachelor's Degree"` |
| `badge` | string | Badge identifier | `"BA"` |
| `color` | string | Color code | `"#1D4ED8"` |
| `description` | string | Level description | `"Undergraduate degree program"` |
| `order` | integer | Display order | `1` |
| `parent_level` | string | Parent level | `null` |
| `slug` | string | URL-friendly identifier | `"bachelors-degree"` |
| `created_date` | datetime | Creation timestamp | `"2024-01-01T00:00:00Z"` |
| `updated_date` | datetime | Last update timestamp | `"2024-01-01T00:00:00Z"` |
| `is_active` | boolean | Active status | `true` |
| `is_deleted` | boolean | Deletion status | `false` |

### Platform Profile Object

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | integer | Primary key | `1` |
| `uuid` | string | Unique identifier | `"550e8400-e29b-41d4-a716-446655440003"` |
| `profile_url` | string | Profile URL | `"https://facebook.com/rupp"` |
| `username` | string | Platform username | `"rupp_official"` |
| `platform` | object | Platform details | `{...}` |
| `school` | integer | School ID | `1` |
| `created_date` | datetime | Creation timestamp | `"2024-01-01T00:00:00Z"` |
| `updated_date` | datetime | Last update timestamp | `"2024-01-01T00:00:00Z"` |
| `is_active` | boolean | Active status | `true` |

## Error Responses

### Common Error Codes

| Status Code | Description | Example |
|-------------|-------------|---------|
| `400` | Bad Request | Invalid data format |
| `401` | Unauthorized | Missing or invalid token |
| `403` | Forbidden | Insufficient permissions |
| `404` | Not Found | School not found |
| `500` | Internal Server Error | Server error |

### Error Response Format

```json
{
  "detail": "Error message",
  "field_name": [
    "Specific field error message"
  ]
}
```

## Rate Limiting

- **Public endpoints:** 1000 requests per hour
- **Authenticated endpoints:** 5000 requests per hour

## File Upload

For logo and cover image uploads:

1. **Use multipart/form-data** for file uploads
2. **Supported formats:** JPG, PNG, GIF
3. **Maximum file size:** 5MB
4. **Image dimensions:** Recommended 800x600 for logos, 1200x800 for covers

### File Upload Example

```bash
curl -X POST \
  -H "Authorization: Bearer <your_token>" \
  -F "name=New School" \
  -F "logo=@/path/to/logo.png" \
  -F "cover_image=@/path/to/cover.jpg" \
  http://localhost:8000/api/v1/schools/
```

## Related Endpoints

### School Types

- `GET /api/v1/school-types/` - List school types
- `POST /api/v1/school-types/` - Create school type
- `GET /api/v1/school-types/{id}/` - Get school type
- `PUT /api/v1/school-types/{id}/` - Update school type
- `DELETE /api/v1/school-types/{id}/` - Delete school type

### Educational Levels

- `GET /api/v1/educational-levels/` - List educational levels
- `POST /api/v1/educational-levels/` - Create educational level
- `GET /api/v1/educational-levels/{id}/` - Get educational level
- `PUT /api/v1/educational-levels/{id}/` - Update educational level
- `DELETE /api/v1/educational-levels/{id}/` - Delete educational level

### Platform Profiles

- `GET /api/v1/platform-profiles/` - List platform profiles
- `POST /api/v1/platform-profiles/` - Create platform profile
- `GET /api/v1/platform-profiles/{id}/` - Get platform profile
- `PUT /api/v1/platform-profiles/{id}/` - Update platform profile
- `DELETE /api/v1/platform-profiles/{id}/` - Delete platform profile

## Testing

### Using curl

```bash
# List schools
curl http://localhost:8000/api/v1/schools/

# Get specific school
curl http://localhost:8000/api/v1/schools/550e8400-e29b-41d4-a716-446655440000/

# Create school (with authentication)
curl -X POST \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test University","short_name":"TU"}' \
  http://localhost:8000/api/v1/schools/

# Update school
curl -X PUT \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Updated University"}' \
  http://localhost:8000/api/v1/schools/550e8400-e29b-41d4-a716-446655440000/

# Delete school
curl -X DELETE \
  -H "Authorization: Bearer <your_token>" \
  http://localhost:8000/api/v1/schools/550e8400-e29b-41d4-a716-446655440000/
```

### Using Swagger UI

Visit `http://localhost:8000/swagger/` for interactive API documentation.

## Notes

1. **Image Fields:** Logo and cover_image fields return `null` when no file is associated
2. **UUID Usage:** All endpoints use UUID for identification instead of integer IDs
3. **Relationships:** Many-to-many relationships are handled through separate endpoints
4. **Filtering:** Use query parameters for filtering and searching
5. **Pagination:** Large result sets are automatically paginated
6. **Caching:** Responses are cached for 5 minutes for public endpoints

## Support

For API support and questions:

- **Email:** <api-support@educationhub.com>
- **Documentation:** <https://docs.educationhub.com/api>
- **GitHub Issues:** <https://github.com/educationhub/api/issues>

## Image Upload and Display (Logo & Cover)

### How It Works

- The `logo` and `cover_image` fields in the School object are string paths (e.g., `/media/logo/filename.png`).
- When retrieving a school, the API returns these as relative URLs.
- The frontend should prepend the backend base URL (e.g., `http://localhost:8000`) if the path does not start with `http`.
- When uploading a new image, use the `/api/v1/upload/` endpoint, then PATCH the school with the returned path (e.g., `logo/filename.png`).

### Example Response

```json
{
  "logo": "/media/logo/13d41bcf-0eee-4d0e-a9e3-34dbb7a87784.png",
  "cover_image": "/media/logo/cover/cover-abc123.png"
}
```

### Frontend Integration

- If `logo` or `cover_image` is not null, display using: `API_BASE_URL + logo`.
- If null, show a placeholder image.

### Troubleshooting

- **Image not displaying?** Ensure the frontend constructs the full URL and the file exists in the backend's `media/` directory.
- **Relative path returned?** This is expected; always prepend the backend URL for display.
- **Null value?** No image is set for this school.

### Upload Flow

1. Upload file to `/api/v1/upload/` (returns a path like `logo/filename.png`).
2. PATCH the school with `{ "logo": "logo/filename.png" }`.
3. On GET, the API returns `/media/logo/filename.png`.
4. Frontend displays as `API_BASE_URL + /media/logo/filename.png`.

---
