# How to Log In and Create Events - Quick Start Guide

## Step 1: Log In to Your Account

### Option A: Navigate to Login Page
1. Open your browser and go to `http://localhost:3000/auth/login`
2. Enter your credentials (email/username and password)
3. Click "Sign In"

### Option B: Social Login
1. Go to `http://localhost:3000/auth/login`
2. Click on "Sign in with Google" or other social providers
3. Authorize and you'll be logged in

### Check if You're Logged In
- After logging in, you should be redirected to the homepage
- You'll see your profile photo/avatar in the top navigation bar
- You can access `/profile/edit` to see your profile

---

## Step 2: Create an Event (Backend API)

Since the frontend UI for event creation isn't built yet, you can create events directly via the API:

### Using Browser/Postman/curl

**1. Start the Backend Server:**
```powershell
cd "d:\Documents\Business\EZ Startup\Apps\EducationHub\Apps\v0.0.2"
.\.venv\Scripts\Activate.ps1
python manage.py runserver
```

**2. Create an Event via POST Request:**

```http
POST http://localhost:8000/api/v1/events/
Content-Type: application/json

{
  "title": "My First Charity Event",
  "description": "A wonderful charity event to support education",
  "event_type": 1,
  "start_datetime": "2025-12-01T10:00:00Z",
  "end_datetime": "2025-12-01T15:00:00Z",
  "country": 1,
  "status": "published",
  "visibility": "public",
  "is_virtual": false
}
```

### Minimum Required Fields:
- `title` - Event name
- `description` - What the event is about
- `event_type` - ID of event type (get from `/api/v1/event-types/`)
- `start_datetime` - When it starts (ISO 8601 format)
- `end_datetime` - When it ends
- `country` - Country ID (get from `/api/v1/countries/`)
- `status` - One of: "draft", "published", "ongoing", "completed", "cancelled"
- `visibility` - One of: "public", "unlisted", "private"

### Optional but Recommended Fields:
- `latitude` & `longitude` - For map display and nearby search
- `city`, `state` - More specific location
- `address` - Street address
- `max_participants` - Capacity limit
- `target_amount` - Fundraising goal
- `tags` - Comma-separated keywords
- `is_featured` - Highlight on homepage
- `is_virtual` - If it's an online event
- `meeting_link` - For virtual events

---

## Step 3: View Your Events

### List All Events:
```http
GET http://localhost:8000/api/v1/events/
```

### Filter Events:
```http
# By status
GET http://localhost:8000/api/v1/events/?status=published

# By location (nearby)
GET http://localhost:8000/api/v1/events/?latitude=13.7563&longitude=100.5018&radius_km=10

# By date range
GET http://localhost:8000/api/v1/events/?start_date_from=2025-11-01&start_date_to=2025-12-31

# Search
GET http://localhost:8000/api/v1/events/?search=charity
```

### Get Event Details:
```http
GET http://localhost:8000/api/v1/events/1/
```

---

## Step 4: Register for an Event

```http
POST http://localhost:8000/api/v1/event-participants/
Content-Type: application/json

{
  "event": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890"
}
```

---

## Step 5: Add Financial Information

### Add a Sponsor:
```http
POST http://localhost:8000/api/v1/event-sponsors/
Content-Type: application/json

{
  "event": 1,
  "sponsor_name": "ABC Company",
  "sponsor_type": "gold",
  "amount_contributed": "10000.00",
  "is_public": true
}
```

### Submit an Expense:
```http
POST http://localhost:8000/api/v1/event-expenses/
Content-Type: application/json

{
  "event": 1,
  "category": "venue",
  "description": "Event hall rental",
  "amount": "2000.00",
  "expense_date": "2025-11-15",
  "status": "pending"
}
```

---

## Frontend Integration (Coming Soon)

The frontend event management UI is currently under development. The following components need to be built:

### What's Ready:
✅ TypeScript types (`src/modules/events/types.ts`)
✅ API clients (`src/modules/events/api/`)
✅ React Query hooks (`src/modules/events/hooks/`)
✅ Zod validation schemas (`src/modules/events/schemas.ts`)
✅ Backend API with full CRUD operations

### What's Needed:
⏳ Event creation form component
⏳ Event list view with filtering
⏳ Event detail page
⏳ Registration form
⏳ Financial transparency dashboard
⏳ Map integration for location

---

## Quick Testing Script

Save this as `test-event-api.http` and use with REST Client extension in VS Code:

```http
### 1. Get Event Types
GET http://localhost:8000/api/v1/event-types/

### 2. Get Countries
GET http://localhost:8000/api/v1/countries/

### 3. Create Event
POST http://localhost:8000/api/v1/events/
Content-Type: application/json

{
  "title": "Test Charity Run",
  "description": "Annual charity run to support schools",
  "event_type": 1,
  "start_datetime": "2025-12-15T08:00:00Z",
  "end_datetime": "2025-12-15T12:00:00Z",
  "latitude": "13.7563",
  "longitude": "100.5018",
  "country": 1,
  "status": "published",
  "visibility": "public",
  "max_participants": 500
}

### 4. List Events
GET http://localhost:8000/api/v1/events/

### 5. Register for Event
POST http://localhost:8000/api/v1/event-participants/
Content-Type: application/json

{
  "event": 1,
  "name": "Test Participant",
  "email": "test@example.com",
  "phone": "+1234567890"
}

### 6. Add Sponsor
POST http://localhost:8000/api/v1/event-sponsors/
Content-Type: application/json

{
  "event": 1,
  "sponsor_name": "Test Sponsor",
  "sponsor_type": "gold",
  "amount_contributed": "5000.00",
  "is_public": true
}
```

---

## Troubleshooting

### Backend Not Starting?
```powershell
# Activate virtual environment
cd "d:\Documents\Business\EZ Startup\Apps\EducationHub\Apps\v0.0.2"
.\.venv\Scripts\Activate.ps1

# Apply migrations
python manage.py migrate

# Start server
python manage.py runserver
```

### Can't Access API Endpoints?
- Make sure backend server is running (`python manage.py runserver`)
- Check URL is `http://localhost:8000` not `https`
- Verify migrations are applied (`python manage.py migrate`)

### Authentication Required?
Some endpoints require authentication. Get auth token:

```http
POST http://localhost:8000/api/v1/token/
Content-Type: application/json

{
  "username": "your_email@example.com",
  "password": "your_password"
}
```

Then use the token in subsequent requests:
```http
GET http://localhost:8000/api/v1/events/
Authorization: Bearer YOUR_ACCESS_TOKEN
```

---

## Next Steps

1. **Test the API**: Use the HTTP examples above to create and manage events
2. **Build the UI**: The frontend components are partially ready, need form implementation
3. **Add Features**: Photos, updates, milestones, feedback as needed

For detailed API documentation, see `docs/EVENT_MANAGEMENT_API_GUIDE.md`
