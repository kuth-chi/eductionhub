# Event Management API - Quick Reference

## Authentication
Most endpoints require authentication via JWT tokens in HttpOnly cookies.

## Base URL
```
/api/v1/
```

## Common Response Formats

### Success
```json
{
  "id": 1,
  "title": "Event Name",
  ...
}
```

### Error
```json
{
  "error": "Error message"
}
```

### Validation Error
```json
{
  "field_name": ["Error message"]
}
```

---

## Events

### List Events
```http
GET /api/v1/events/
```
**Query Parameters:**
- `event_type` - Filter by type ID
- `status` - draft|published|ongoing|completed|cancelled
- `visibility` - public|unlisted|private
- `country`, `state`, `city` - Location filters
- `is_virtual` - true|false
- `is_featured` - true|false
- `start_date_from` - ISO datetime
- `start_date_to` - ISO datetime
- `latitude`, `longitude`, `radius_km` - Proximity search
- `search` - Full text search
- `ordering` - start_datetime|created_at|title (prefix with `-` for desc)

### Get Event Details
```http
GET /api/v1/events/{id}/
GET /api/v1/events/by-slug/{slug}/
```

### Create Event
```http
POST /api/v1/events/
Authorization: Bearer {token}
```
**Body:**
```json
{
  "title": "Annual Tech Conference",
  "slug": "annual-tech-conference-2025",
  "description": "Full description here...",
  "short_description": "Brief summary",
  "event_type": 1,
  "country": 1,
  "state": 1,
  "city": 1,
  "address_line_1": "123 Main St",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "start_datetime": "2025-06-15T09:00:00Z",
  "end_datetime": "2025-06-15T17:00:00Z",
  "max_participants": 500,
  "requires_approval": false,
  "status": "draft"
}
```

### Update Event
```http
PUT /api/v1/events/{id}/
PATCH /api/v1/events/{id}/
Authorization: Bearer {token}
```
Requires: `can_edit_event` permission

### Delete Event
```http
DELETE /api/v1/events/{id}/
Authorization: Bearer {token}
```
Requires: Owner only

### Publish Event
```http
POST /api/v1/events/{id}/publish/
Authorization: Bearer {token}
```

### Cancel Event
```http
POST /api/v1/events/{id}/cancel/
Authorization: Bearer {token}
```
Requires: Owner only

### Get My Events
```http
GET /api/v1/events/my_events/
Authorization: Bearer {token}
```

### Management Dashboard
```http
GET /api/v1/events/{id}/management_dashboard/
Authorization: Bearer {token}
```
Requires: `can_edit_event` permission

---

## Organizers

### List Event Organizers
```http
GET /api/v1/event-organizers/?event={event_id}
Authorization: Bearer {token}
```

### Invite Organizer
```http
POST /api/v1/event-organizers/invite_organizer/
Authorization: Bearer {token}
```
**Body:**
```json
{
  "event": 1,
  "user": 2,
  "role": "co-organizer",
  "can_edit_event": false,
  "can_manage_participants": true,
  "can_manage_finances": false,
  "can_upload_media": true,
  "can_post_updates": true
}
```
Requires: Owner or Lead Organizer

### Update Organizer Permissions
```http
PATCH /api/v1/event-organizers/{id}/update_permissions/
Authorization: Bearer {token}
```
**Body:**
```json
{
  "role": "lead",
  "can_edit_event": true,
  "can_manage_participants": true
}
```

### Remove Organizer
```http
DELETE /api/v1/event-organizers/{id}/
Authorization: Bearer {token}
```

---

## Participants

### Register for Event (Guest)
```http
POST /api/v1/event-participants/register/
```
**Body:**
```json
{
  "event": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "organization_name": "Acme Corp",
  "special_requirements": "Vegetarian meal"
}
```

### Register (Authenticated)
```http
POST /api/v1/event-participants/
Authorization: Bearer {token}
```
**Body:** (name/email auto-filled from user)
```json
{
  "event": 1,
  "special_requirements": "Wheelchair access needed"
}
```

### My Registrations
```http
GET /api/v1/event-participants/my_registrations/
Authorization: Bearer {token}
```

### List Event Participants
```http
GET /api/v1/event-participants/?event={event_id}
Authorization: Bearer {token}
```
Requires: `can_manage_participants` permission

### Confirm Registration
```http
POST /api/v1/event-participants/{id}/confirm/
Authorization: Bearer {token}
```

### Reject Registration
```http
POST /api/v1/event-participants/{id}/reject/
Authorization: Bearer {token}
```
**Body:**
```json
{
  "reason": "Event is full"
}
```

### Check-in Participant
```http
POST /api/v1/event-participants/{id}/check_in/
Authorization: Bearer {token}
```

### Bulk Check-in
```http
POST /api/v1/event-participants/bulk_check_in/
Authorization: Bearer {token}
```
**Body:**
```json
{
  "event": 1,
  "participant_ids": [1, 2, 3, 4, 5]
}
```

### Cancel Registration
```http
POST /api/v1/event-participants/{id}/cancel/
Authorization: Bearer {token}
```

---

## Sponsors

### List Sponsors
```http
GET /api/v1/event-sponsors/?event={event_id}
```

### Register as Sponsor
```http
POST /api/v1/event-sponsors/register_as_sponsor/
Authorization: Bearer {token}
```
**Body:**
```json
{
  "event": 1,
  "organization": 5,
  "sponsor_name": "TechCorp Inc",
  "sponsor_type": "gold",
  "contribution_amount": 10000.00,
  "contribution_description": "Gold tier sponsorship"
}
```

### Add Sponsor (Direct)
```http
POST /api/v1/event-sponsors/
Authorization: Bearer {token}
```
Requires: `can_manage_finances` permission

### Approve Sponsor
```http
POST /api/v1/event-sponsors/{id}/approve/
Authorization: Bearer {token}
```

### Reject Sponsor
```http
POST /api/v1/event-sponsors/{id}/reject/
Authorization: Bearer {token}
```

---

## Expenses

### List Expenses
```http
GET /api/v1/event-expenses/?event={event_id}
Authorization: Bearer {token}
```
Requires: `can_manage_finances` permission

### Create Expense
```http
POST /api/v1/event-expenses/
Authorization: Bearer {token}
```
**Body:**
```json
{
  "event": 1,
  "category": "venue",
  "title": "Venue Rental",
  "description": "Main conference hall rental for 2 days",
  "amount": 5000.00,
  "currency": "USD",
  "expense_date": "2025-05-15",
  "vendor_name": "City Convention Center"
}
```

### Approve Expense
```http
POST /api/v1/event-expenses/{id}/approve/
Authorization: Bearer {token}
```
**Body:**
```json
{
  "notes": "Approved by finance committee"
}
```

### Reject Expense
```http
POST /api/v1/event-expenses/{id}/reject/
Authorization: Bearer {token}
```
**Body:**
```json
{
  "reason": "Exceeds budget allocation"
}
```

### Mark Paid
```http
POST /api/v1/event-expenses/{id}/mark_paid/
Authorization: Bearer {token}
```
**Body:**
```json
{
  "payment_date": "2025-05-20"
}
```

---

## Media

### Upload Photo
```http
POST /api/v1/event-photos/
Authorization: Bearer {token}
Content-Type: multipart/form-data
```
**Body:**
```
event=1
image=<file>
caption=Amazing event moment
is_public=true
is_featured=false
```
Requires: `can_upload_media` permission

### List Photos
```http
GET /api/v1/event-photos/?event={event_id}
```

---

## Updates

### Post Update
```http
POST /api/v1/event-updates/
Authorization: Bearer {token}
```
**Body:**
```json
{
  "event": 1,
  "update_type": "announcement",
  "title": "Schedule Change",
  "content": "Morning session moved to 10 AM",
  "is_public": true,
  "is_pinned": false
}
```
Requires: `can_post_updates` permission

### List Updates
```http
GET /api/v1/event-updates/?event={event_id}
```

---

## Feedback

### Submit Feedback
```http
POST /api/v1/event-feedback/
Authorization: Bearer {token}
```
**Body:**
```json
{
  "event": 1,
  "participant": 10,
  "rating": 5,
  "feedback_text": "Excellent organization and content!",
  "is_public": true
}
```

---

## Status Codes

- `200 OK` - Success
- `201 Created` - Resource created
- `204 No Content` - Success (no body)
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Not authenticated
- `403 Forbidden` - No permission
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

## Permission Quick Reference

| Action | Required Permission | Who Has It |
|--------|-------------------|------------|
| Create Event | Authenticated | Any user |
| Edit Event | `can_edit_event` | Owner, Lead, authorized co-organizers |
| Delete Event | Owner | Owner only |
| Manage Organizers | Owner or Lead | Owner, Lead organizers |
| Manage Participants | `can_manage_participants` | Owner, authorized organizers |
| Manage Finances | `can_manage_finances` | Owner, finance managers |
| Upload Media | `can_upload_media` | Owner, authorized organizers |
| Post Updates | `can_post_updates` | Owner, authorized organizers |
| Register | None (public) | Anyone |
| Sponsor Registration | Authenticated | Any authenticated user |

---

## Rate Limiting
Standard rate limits apply. Contact admin for higher limits.

## Support
For issues or questions, contact: support@educationhub.com
