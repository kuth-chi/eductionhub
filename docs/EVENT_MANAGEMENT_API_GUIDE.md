# Event Management API Guide

## Overview

Complete REST API for event management with geolocation, financial transparency, and flexible global operations.

## Backend Status

✅ **COMPLETED:**
- 14 Django models with geolocation support
- Complete serializers for all entities
- ViewSets with CRUD operations
- API routes registered in `api/urls.py`
- Migrations created (0001_initial.py)

## API Endpoints

All endpoints are prefixed with `/api/v1/`

### Event Categories & Types
- `GET /api/v1/event-categories/` - List all categories
- `GET /api/v1/event-types/` - List all event types
- `GET /api/v1/event-types/?category={id}` - Filter by category

### Events
- `GET /api/v1/events/` - List all events
- `POST /api/v1/events/` - Create new event
- `GET /api/v1/events/{id}/` - Get event details
- `PUT /api/v1/events/{id}/` - Update event
- `DELETE /api/v1/events/{id}/` - Delete event
- `GET /api/v1/events/by_slug/?slug={slug}` - Get event by slug

#### Query Parameters
- `latitude`, `longitude`, `radius_km` - Find nearby events
- `event_type` - Filter by event type
- `status` - Filter by status (draft, published, ongoing, completed, cancelled)
- `visibility` - Filter by visibility (public, unlisted, private)
- `country`, `state`, `city` - Filter by location
- `is_virtual` - Filter virtual events
- `is_featured` - Filter featured events
- `start_date_from`, `start_date_to` - Filter by date range
- `search` - Search in title, description, tags
- `ordering` - Sort by: start_datetime, created_at, title

### Event Participants
- `GET /api/v1/event-participants/` - List participants
- `POST /api/v1/event-participants/` - Register for event
- `GET /api/v1/event-participants/{id}/` - Get participant details
- `POST /api/v1/event-participants/{id}/check_in/` - Check in participant
- `POST /api/v1/event-participants/{id}/check_out/` - Check out participant
- `POST /api/v1/event-participants/{id}/confirm/` - Confirm registration
- `POST /api/v1/event-participants/{id}/cancel/` - Cancel registration
- `GET /api/v1/event-participants/my_registrations/` - Get current user's registrations (auth required)

### Financial Transparency

#### Sponsors
- `GET /api/v1/event-sponsors/` - List sponsors
- `POST /api/v1/event-sponsors/` - Add sponsor
- `GET /api/v1/event-sponsors/{id}/` - Get sponsor details
- `PUT /api/v1/event-sponsors/{id}/` - Update sponsor
- `DELETE /api/v1/event-sponsors/{id}/` - Remove sponsor

#### Expenses
- `GET /api/v1/event-expenses/` - List expenses
- `POST /api/v1/event-expenses/` - Submit expense
- `GET /api/v1/event-expenses/{id}/` - Get expense details
- `PUT /api/v1/event-expenses/{id}/` - Update expense
- `DELETE /api/v1/event-expenses/{id}/` - Delete expense
- `POST /api/v1/event-expenses/{id}/approve/` - Approve expense (auth required)
- `POST /api/v1/event-expenses/{id}/reject/` - Reject expense (auth required)

### Tickets
- `GET /api/v1/event-tickets/` - List tickets
- `POST /api/v1/event-tickets/` - Create ticket type
- `GET /api/v1/event-tickets/{id}/` - Get ticket details
- `PUT /api/v1/event-tickets/{id}/` - Update ticket
- `DELETE /api/v1/event-tickets/{id}/` - Delete ticket

### Media & Updates
- `GET /api/v1/event-photos/` - List photos
- `POST /api/v1/event-photos/` - Upload photo
- `GET /api/v1/event-updates/` - List updates
- `POST /api/v1/event-updates/` - Post update
- `GET /api/v1/event-milestones/` - List milestones
- `POST /api/v1/event-milestones/{id}/complete/` - Mark milestone complete
- `GET /api/v1/event-feedback/` - List feedback
- `POST /api/v1/event-feedback/` - Submit feedback

## Creating an Event

### 1. Start Backend Server

```bash
cd "d:\Documents\Business\EZ Startup\Apps\EducationHub\Apps\v0.0.2"
.\.venv\Scripts\Activate.ps1
python manage.py runserver
```

### 2. Create Event via API

**Request:**
```http
POST http://localhost:8000/api/v1/events/
Content-Type: application/json

{
  "title": "Charity Run for Education",
  "slug": "charity-run-2024",
  "description": "Annual charity run to support school supplies",
  "event_type": 1,
  "start_datetime": "2024-06-15T08:00:00Z",
  "end_datetime": "2024-06-15T12:00:00Z",
  "latitude": "13.7563",
  "longitude": "100.5018",
  "address": "Lumphini Park",
  "city": 1,
  "country": 1,
  "is_virtual": false,
  "status": "published",
  "visibility": "public",
  "max_participants": 500,
  "registration_deadline": "2024-06-10T23:59:59Z",
  "target_amount": "50000.00",
  "tags": "charity,education,running,fitness"
}
```

### 3. Register for Event

**Request:**
```http
POST http://localhost:8000/api/v1/event-participants/
Content-Type: application/json

{
  "event": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "organization_name": "ABC Company",
  "special_requirements": "Vegetarian meal"
}
```

### 4. Add Sponsor

**Request:**
```http
POST http://localhost:8000/api/v1/event-sponsors/
Content-Type: application/json

{
  "event": 1,
  "organization": 1,
  "sponsor_type": "gold",
  "amount_contributed": "10000.00",
  "is_public": true
}
```

### 5. Submit Expense

**Request:**
```http
POST http://localhost:8000/api/v1/event-expenses/
Content-Type: application/json

{
  "event": 1,
  "category": "venue",
  "description": "Park rental fee",
  "amount": "2000.00",
  "expense_date": "2024-06-01",
  "status": "pending"
}
```

## Frontend Integration

The frontend is ready with:
- TypeScript types (`src/modules/events/types.ts`)
- Zod schemas (`src/modules/events/schemas.ts`)
- API clients (`src/modules/events/api/`)
- React Query hooks (`src/modules/events/hooks/`)
- Geolocation services

### Using API Clients

```typescript
import { eventsApi } from '@/modules/events/api/events-client'

// Create event
const newEvent = await eventsApi.create({
  title: "My Event",
  // ... other fields
})

// Search nearby events
const nearbyEvents = await eventsApi.searchNearby({
  latitude: 13.7563,
  longitude: 100.5018,
  radiusKm: 10
})
```

### Using React Query Hooks

```typescript
import { useEvents, useCreateEvent } from '@/modules/events/hooks/events-hooks'

function EventList() {
  const { data: events, isLoading } = useEvents()
  const createMutation = useCreateEvent()
  
  const handleCreate = async (data) => {
    await createMutation.mutateAsync(data)
  }
  
  return <div>{/* UI */}</div>
}
```

## Geolocation Features

### Finding Nearby Events

Events can be filtered by proximity using latitude, longitude, and radius:

```http
GET /api/v1/events/?latitude=13.7563&longitude=100.5018&radius_km=10
```

This uses a bounding box filter for efficient queries on large datasets.

### Distance Calculation

The frontend includes a Haversine distance calculator:

```typescript
import { calculateDistance } from '@/modules/events/services/distance-calculator'

const distance = calculateDistance(
  { lat: 13.7563, lng: 100.5018 },
  { lat: 13.7500, lng: 100.5000 }
) // Returns distance in km
```

## Financial Transparency

Events track all financial data:
- **Sponsors**: Organizations contributing funds
- **Expenses**: All expenditures with approval workflow
- **Target Amount**: Fundraising goal
- **Current Amount**: Real-time total from sponsors
- **Funding Percentage**: Auto-calculated progress

### Example: Check Funding Status

```http
GET /api/v1/events/1/
```

Response includes:
```json
{
  "target_amount": "50000.00",
  "current_amount": "35000.00",
  "funding_percentage": 70.0,
  "sponsors_count": 5
}
```

## Next Steps

1. **Test Backend API**: Start server and test endpoints with curl/Postman
2. **Build UI Components**: Create event cards, forms, maps
3. **Build Page Views**: List view, detail view, create form
4. **Add Map Integration**: Display events on interactive map
5. **Implement Notifications**: Email confirmations, reminders

## Model Reference

### Event Model Fields
- Basic info: title, slug, description, event_type
- DateTime: start_datetime, end_datetime, timezone_name
- Location: latitude, longitude, address, city, state, country, village
- Virtual: is_virtual, meeting_link
- Registration: max_participants, registration_deadline, registration_requirements
- Financial: target_amount (auto-calculates current_amount)
- Status: status, visibility, is_featured
- Relations: target_school, target_organization
- Computed: is_registration_open, is_full, funding_percentage

### Event Status Options
- `draft` - Not published
- `published` - Live and visible
- `ongoing` - Currently happening
- `completed` - Finished
- `cancelled` - Cancelled

### Event Visibility
- `public` - Visible to all
- `unlisted` - Only via direct link
- `private` - Invitation only

## Troubleshooting

### Migration Not Applied

```bash
python manage.py migrate event
```

### Import Errors

Ensure virtual environment is activated:
```bash
.\.venv\Scripts\Activate.ps1
```

### CORS Issues

Frontend must use `authFetch` from `@/lib/auth-fetch` which handles cookies and CORS.

---

**API is ready!** Start the backend server and you can create events immediately.
