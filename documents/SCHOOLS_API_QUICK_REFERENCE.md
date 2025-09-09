# Schools API Quick Reference

## Base URL

`http://localhost:8000/api/v1/`

## Authentication

- **Public:** GET endpoints
- **Protected:** POST, PUT, PATCH, DELETE endpoints require JWT token
- **Header:** `Authorization: Bearer <token>`

## Endpoints

### Schools

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/schools/` | List all schools | No |
| GET | `/schools/{uuid}/` | Get specific school | No |
| POST | `/schools/` | Create school | Yes |
| PUT | `/schools/{uuid}/` | Update school | Yes |
| PATCH | `/schools/{uuid}/` | Partial update | Yes |
| DELETE | `/schools/{uuid}/` | Delete school | Yes |
| GET | `/schools/{uuid}/analytics/` | Get analytics | No |

### Query Parameters (List Schools)

| Parameter | Example | Description |
|-----------|---------|-------------|
| `search` | `?search=university` | Search by name, local_name, president, founder |
| `type` | `?type=1` | Filter by school type ID |
| `create_date` | `?create_date=2024-01-01` | Filter by creation date |
| `ordering` | `?ordering=name` | Sort by field |

## Request Examples

### Create School

```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New University",
    "short_name": "NU",
    "description": "A new educational institution",
    "type_ids": [1, 2],
    "educational_level_ids": [1, 2]
  }' \
  http://localhost:8000/api/v1/schools/
```

### Update School

```bash
curl -X PATCH \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "tuition": "950.00",
    "description": "Updated description"
  }' \
  http://localhost:8000/api/v1/schools/550e8400-e29b-41d4-a716-446655440000/
```

### File Upload

```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -F "name=New School" \
  -F "logo=@/path/to/logo.png" \
  -F "cover_image=@/path/to/cover.jpg" \
  http://localhost:8000/api/v1/schools/
```

## Response Fields

### School Object

```json
{
  "pk": 1,
  "uuid": "550e8400-e29b-41d4-a716-446655440000",
  "name": "School Name",
  "local_name": "Local Name",
  "logo": "/media/uploads/schools/logos/logo.png",
  "cover_image": "/media/uploads/schools/cover/cover.jpg",
  "short_name": "SN",
  "code": "CODE001",
  "description": "School description",
  "founder": "Founder name",
  "president": "President name",
  "established": "1960-01-01",
  "street_address": "Street address",
  "address_line_2": "Additional address",
  "box_number": "P.O. Box 1234",
  "postal_code": "12345",
  "country": 1,
  "state": 1,
  "city": 1,
  "village": null,
  "location": "Location string",
  "motto": "School motto",
  "tuition": "500.00",
  "endowment": "1000000.00",
  "created_date": "2024-01-15T10:30:00Z",
  "updated_date": "2024-01-15T10:30:00Z",
  "slug": "school-slug",
  "is_active": true,
  "self_data": "Custom data",
  "type": [...],
  "educational_levels": [...],
  "platform_profiles": [...]
}
```

## Related Endpoints

### School Types

- `GET /school-types/` - List types
- `POST /school-types/` - Create type
- `GET /school-types/{id}/` - Get type
- `PUT /school-types/{id}/` - Update type
- `DELETE /school-types/{id}/` - Delete type

### Educational Levels

- `GET /educational-levels/` - List levels
- `POST /educational-levels/` - Create level
- `GET /educational-levels/{id}/` - Get level
- `PUT /educational-levels/{id}/` - Update level
- `DELETE /educational-levels/{id}/` - Delete level

### Platform Profiles

- `GET /platform-profiles/` - List profiles
- `POST /platform-profiles/` - Create profile
- `GET /platform-profiles/{id}/` - Get profile
- `PUT /platform-profiles/{id}/` - Update profile
- `DELETE /platform-profiles/{id}/` - Delete profile

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 204 | No Content (Delete) |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 500 | Internal Server Error |

## Notes

- **Image fields** return `null` when no file is associated
- **UUID** is used for identification instead of integer IDs
- **File uploads** use `multipart/form-data`
- **Supported formats:** JPG, PNG, GIF (max 5MB)
- **Swagger UI:** `http://localhost:8000/swagger/`

## Image Fields (Logo & Cover)

- `logo` and `cover_image` are string paths (e.g., `/media/logo/filename.png`).
- To display, use: `API_BASE_URL + logo`.
- If null, show a placeholder image.

## Troubleshooting

- If the image does not display, check that the path is correct and prepend the backend URL if needed.
