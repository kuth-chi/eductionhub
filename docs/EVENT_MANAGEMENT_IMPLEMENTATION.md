# Event Management System - Full Implementation

## Overview

This document describes the complete event management system with role-based permissions for Event Owners, Organizers, Co-Organizers, Visitors/Participants, and Sponsors.

## User Roles & Permissions

### 1. Event Owner (Creator)
**Full control over all event aspects**

- Create, edit, and delete events
- Manage all organizers (add, remove, update permissions)
- Manage participants (approve, reject, check-in)
- Manage finances (sponsors, expenses)
- Post updates and upload media
- Access management dashboard
- Publish/cancel events

**API Endpoints:**
- `POST /api/v1/events/` - Create event
- `PUT/PATCH /api/v1/events/{id}/` - Update event
- `DELETE /api/v1/events/{id}/` - Delete event
- `POST /api/v1/events/{id}/publish/` - Publish event
- `POST /api/v1/events/{id}/cancel/` - Cancel event
- `GET /api/v1/events/{id}/management_dashboard/` - View dashboard
- All organizer management endpoints

### 2. Lead Organizer
**Team management and event editing rights**

Permissions:
- Edit event details
- Manage other organizers (add/remove co-organizers)
- Manage participants
- Manage finances
- Post updates
- Upload media

**API Endpoints:**
- `POST /api/v1/event-organizers/invite_organizer/` - Invite organizers
- `PATCH /api/v1/event-organizers/{id}/update_permissions/` - Update permissions
- `DELETE /api/v1/event-organizers/{id}/` - Remove organizers
- All participant management endpoints
- All financial management endpoints

### 3. Co-Organizer
**Specialized roles based on assigned permissions**

Types:
- **Volunteer Coordinator** - Can manage participants
- **Finance Manager** - Can manage sponsors and expenses
- **Media Manager** - Can upload photos and post updates
- **Logistics Manager** - Custom permissions
- **Registration Manager** - Can manage participant registrations

Permissions (granular):
- `can_edit_event` - Edit event details
- `can_manage_participants` - Approve/reject registrations, check-in
- `can_manage_finances` - Add sponsors, manage expenses
- `can_upload_media` - Upload photos
- `can_post_updates` - Post announcements

**API Endpoints:**
Based on assigned permissions:
- `GET /api/v1/event-organizers/my_events/` - View organized events
- Participant management (if `can_manage_participants`)
- Financial management (if `can_manage_finances`)
- Media uploads (if `can_upload_media`)
- Updates posting (if `can_post_updates`)

### 4. Visitor/Participant
**Public event registration and participation**

Capabilities:
- Browse public events
- Register for events (authenticated or guest)
- View registration status
- Cancel own registration
- Provide feedback after attendance

**API Endpoints:**
- `GET /api/v1/events/` - Browse events
- `GET /api/v1/events/{id}/` - View event details
- `GET /api/v1/events/by-slug/{slug}/` - View by slug
- `POST /api/v1/event-participants/register/` - Register (guest/visitor)
- `POST /api/v1/event-participants/` - Register (authenticated)
- `GET /api/v1/event-participants/my_registrations/` - View registrations
- `POST /api/v1/event-participants/{id}/cancel/` - Cancel registration
- `POST /api/v1/event-feedback/` - Submit feedback

### 5. Sponsor
**Organization or individual sponsorship**

Capabilities:
- View public events
- Register as sponsor
- View sponsorship status
- Update sponsorship details (pending approval)

**API Endpoints:**
- `POST /api/v1/event-sponsors/register_as_sponsor/` - Self-register as sponsor
- `GET /api/v1/event-sponsors/?event={id}` - View event sponsors
- Organizers approve/reject via:
  - `POST /api/v1/event-sponsors/{id}/approve/`
  - `POST /api/v1/event-sponsors/{id}/reject/`

## Permission System Architecture

### Permission Helper Module
Location: `event/permissions.py`

**Key Functions:**
```python
EventPermissionChecker.is_event_owner(user, event)
EventPermissionChecker.is_lead_organizer(user, event)
EventPermissionChecker.is_organizer(user, event)
EventPermissionChecker.can_edit_event(user, event)
EventPermissionChecker.can_manage_participants(user, event)
EventPermissionChecker.can_manage_finances(user, event)
EventPermissionChecker.can_manage_organizers(user, event)
EventPermissionChecker.can_post_updates(user, event)
EventPermissionChecker.can_upload_media(user, event)

# Raise PermissionDenied if not authorized
EventPermissionChecker.require_event_owner(user, event)
EventPermissionChecker.require_edit_permission(user, event)
# ... etc
```

**Get User Permissions:**
```python
permissions = get_user_event_permissions(user, event)
# Returns:
{
    'is_owner': bool,
    'is_lead_organizer': bool,
    'is_organizer': bool,
    'can_edit_event': bool,
    'can_manage_participants': bool,
    'can_manage_finances': bool,
    'can_manage_organizers': bool,
    'can_post_updates': bool,
    'can_upload_media': bool,
    'role': str  # 'owner', 'lead', 'co-organizer', etc.
}
```

## API Endpoints Reference

### Event Management

#### Public Endpoints (No Auth Required)
```
GET    /api/v1/events/                     # List public events
GET    /api/v1/events/{id}/                # Event details
GET    /api/v1/events/by-slug/{slug}/      # Event by slug
GET    /api/v1/event-categories/           # Event categories
GET    /api/v1/event-types/                # Event types
```

#### Authenticated User Endpoints
```
POST   /api/v1/events/                     # Create event (becomes owner)
GET    /api/v1/events/my_events/           # My owned/organized events
```

#### Owner/Organizer Endpoints
```
PUT    /api/v1/events/{id}/                # Update event (requires can_edit_event)
DELETE /api/v1/events/{id}/                # Delete event (owner only)
POST   /api/v1/events/{id}/publish/        # Publish draft (requires can_edit_event)
POST   /api/v1/events/{id}/cancel/         # Cancel event (owner only)
GET    /api/v1/events/{id}/management_dashboard/  # Dashboard (requires can_edit_event)
GET    /api/v1/events/{id}/participants_list/     # Participants (filtered by permissions)
```

### Organizer Management

```
GET    /api/v1/event-organizers/?event={id}       # List organizers
POST   /api/v1/event-organizers/invite_organizer/ # Invite (owner/lead only)
PATCH  /api/v1/event-organizers/{id}/update_permissions/  # Update (owner/lead only)
DELETE /api/v1/event-organizers/{id}/              # Remove (owner/lead only)
GET    /api/v1/event-organizers/my_events/        # My organized events
```

### Participant Management

#### Public/Visitor Registration
```
POST   /api/v1/event-participants/register/       # Guest registration (no auth)
POST   /api/v1/event-participants/                # Authenticated registration
```

#### Authenticated User
```
GET    /api/v1/event-participants/my_registrations/  # My registrations
POST   /api/v1/event-participants/{id}/cancel/       # Cancel own registration
```

#### Organizer Actions (requires can_manage_participants)
```
GET    /api/v1/event-participants/?event={id}      # List participants
POST   /api/v1/event-participants/{id}/confirm/    # Confirm registration
POST   /api/v1/event-participants/{id}/reject/     # Reject registration
POST   /api/v1/event-participants/{id}/check_in/   # Check-in participant
POST   /api/v1/event-participants/{id}/check_out/  # Check-out participant
POST   /api/v1/event-participants/bulk_check_in/   # Bulk check-in
```

### Sponsor Management

#### Public
```
GET    /api/v1/event-sponsors/?event={id}          # View public sponsors
```

#### Sponsor Self-Registration
```
POST   /api/v1/event-sponsors/register_as_sponsor/ # Self-register as sponsor
```

#### Organizer Actions (requires can_manage_finances)
```
POST   /api/v1/event-sponsors/                     # Add sponsor (direct)
PUT    /api/v1/event-sponsors/{id}/                # Update sponsor
DELETE /api/v1/event-sponsors/{id}/                # Remove sponsor
POST   /api/v1/event-sponsors/{id}/approve/        # Approve sponsor registration
POST   /api/v1/event-sponsors/{id}/reject/         # Reject sponsor registration
```

### Financial Management (requires can_manage_finances)

```
GET    /api/v1/event-expenses/?event={id}          # List expenses
POST   /api/v1/event-expenses/                     # Create expense
PUT    /api/v1/event-expenses/{id}/                # Update expense
DELETE /api/v1/event-expenses/{id}/                # Delete expense
POST   /api/v1/event-expenses/{id}/approve/        # Approve expense
POST   /api/v1/event-expenses/{id}/reject/         # Reject expense
POST   /api/v1/event-expenses/{id}/mark_paid/      # Mark as paid
```

### Media & Updates

#### Public
```
GET    /api/v1/event-photos/?event={id}            # View public photos
GET    /api/v1/event-updates/?event={id}           # View public updates
```

#### Organizer Actions
```
POST   /api/v1/event-photos/                       # Upload (requires can_upload_media)
POST   /api/v1/event-updates/                      # Post update (requires can_post_updates)
PUT    /api/v1/event-photos/{id}/                  # Update photo
DELETE /api/v1/event-photos/{id}/                  # Delete photo
PUT    /api/v1/event-updates/{id}/                 # Update announcement
DELETE /api/v1/event-updates/{id}/                 # Delete announcement
```

### Milestones & Feedback

```
GET    /api/v1/event-milestones/?event={id}        # View milestones
POST   /api/v1/event-milestones/                   # Create (requires can_edit_event)
POST   /api/v1/event-milestones/{id}/complete/     # Mark complete (requires can_edit_event)
POST   /api/v1/event-feedback/                     # Submit feedback (authenticated)
```

## Workflow Examples

### 1. Creating an Event (Owner Flow)
```
1. POST /api/v1/events/ (user becomes owner)
2. POST /api/v1/event-organizers/invite_organizer/ (add team)
3. POST /api/v1/event-tickets/ (setup tickets)
4. POST /api/v1/events/{id}/publish/ (make live)
```

### 2. Visitor Registration Flow
```
1. GET /api/v1/events/ (browse events)
2. GET /api/v1/events/{id}/ (view details)
3. POST /api/v1/event-participants/register/ (register - guest or auth)
4. [Organizer] POST /api/v1/event-participants/{id}/confirm/ (if approval required)
5. [Day of event] Organizer checks in participant
```

### 3. Sponsor Registration Flow
```
1. GET /api/v1/events/{id}/ (view event)
2. POST /api/v1/event-sponsors/register_as_sponsor/ (submit sponsorship)
3. [Organizer] Reviews submission
4. [Organizer] POST /api/v1/event-sponsors/{id}/approve/ (approve)
```

### 4. Co-Organizer Management Flow
```
1. [Owner] POST /api/v1/event-organizers/invite_organizer/
2. [Owner] PATCH /api/v1/event-organizers/{id}/update_permissions/
   {
     "can_manage_participants": true,
     "can_post_updates": true
   }
3. [Co-Organizer] Can now manage participants and post updates
```

## Event Management Dashboard

**Endpoint:** `GET /api/v1/events/{id}/management_dashboard/`

**Response:**
```json
{
  "event": { /* full event details */ },
  "user_permissions": {
    "is_owner": true,
    "can_edit_event": true,
    "can_manage_participants": true,
    // ... all permissions
  },
  "statistics": {
    "total_participants": 150,
    "confirmed_participants": 120,
    "attended_participants": 85,
    "waitlist_count": 10,
    "total_sponsors": 5,
    "total_sponsorship": 50000.00,
    "total_expenses": 35000.00,
    "pending_expenses": 3
  },
  "recent_participants": [ /* last 10 registrations */ ],
  "organizers": [ /* all organizers with roles */ ]
}
```

## Security Considerations

1. **Permission Checks**: All modify operations check permissions before execution
2. **Owner Protection**: Only owner can delete events or remove the last lead organizer
3. **Financial Transparency**: Finance management requires explicit permission
4. **Privacy**: Participant details filtered based on permissions
5. **Guest Registration**: Email validation and duplicate prevention

## Frontend Integration

### Checking User Permissions
```javascript
// Get event with user permissions
const response = await fetch(`/api/v1/events/by-slug/${slug}/`);
const { user_permissions } = await response.json();

// Show/hide UI based on permissions
{user_permissions?.can_edit_event && <EditButton />}
{user_permissions?.can_manage_participants && <ParticipantManager />}
```

### Event Registration Form
```javascript
// Guest or authenticated
await fetch('/api/v1/event-participants/register/', {
  method: 'POST',
  body: JSON.stringify({
    event: eventId,
    name: "John Doe",
    email: "john@example.com",
    phone: "+1234567890",
    special_requirements: "Vegetarian meal"
  })
});
```

### Sponsor Registration
```javascript
await fetch('/api/v1/event-sponsors/register_as_sponsor/', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` },
  body: JSON.stringify({
    event: eventId,
    organization: orgId, // optional
    sponsor_name: "Acme Corp",
    sponsor_type: "gold",
    contribution_amount: 10000.00,
    contribution_description: "Gold sponsorship package"
  })
});
```

## Database Models

Key models involved:
- `Event` - Core event entity with `created_by` field
- `EventOrganizer` - Team members with granular permissions
- `EventParticipant` - Registrations and attendance tracking
- `EventSponsor` - Sponsorship records
- `EventExpense` - Financial tracking with approval workflow
- `EventPhoto` - Media gallery
- `EventUpdate` - Announcements
- `EventMilestone` - Progress tracking
- `EventFeedback` - Post-event reviews

## Testing Checklist

- [ ] Event creation sets correct owner
- [ ] Only owner can delete events
- [ ] Lead organizers can add/remove co-organizers
- [ ] Co-organizers permissions are enforced
- [ ] Visitors can register without authentication
- [ ] Authenticated users auto-linked to registrations
- [ ] Sponsors can self-register
- [ ] Finance permissions properly enforced
- [ ] Management dashboard shows correct statistics
- [ ] Public vs private content filtering works
- [ ] Cannot remove last lead organizer
- [ ] Cancellation properly updates status

## Future Enhancements

1. Email notifications for all key actions
2. Calendar integration (iCal/Google Calendar)
3. QR code generation for check-ins
4. Payment processing for tickets
5. Automated reminder emails
6. Analytics and reporting
7. Event templates
8. Recurring events
9. Multi-language support
10. Social media integration
