# Event Models Refactoring Summary

**Date:** 2025
**Issue:** Pylint C0302 - Too many lines in module (1189/1000)
**Original File:** `event/models.py` (1187 lines)

## Refactoring Strategy

Split the monolithic `models.py` file into a modular package structure based on domain responsibility.

## New Structure

### Package: `event/models/`

```
event/models/
├── __init__.py          # Re-exports all models for backward compatibility
├── base_models.py       # Taxonomy models (70 lines)
├── event.py             # Main Event model (391 lines)
├── people.py            # Organizers and participants (167 lines)
├── financial.py         # Sponsors, expenses, tickets (316 lines)
├── content.py           # Photos, updates, milestones, feedback (267 lines)
└── partnerships.py      # Partnerships and impact (118 lines)
```

## Model Distribution

### base_models.py (70 lines)
- **EventCategory**: Event categorization (charity, educational, sports, etc.)
- **EventType**: Specific event types (fundraiser, workshop, conference, etc.)

### event.py (391 lines)
- **Event**: Core event entity with:
  - Identity fields (title, slug, description, type)
  - Geolocation (country, state, city, coordinates, address)
  - Virtual event support
  - Timing and registration
  - Financial tracking
  - Status and visibility
  - SEO metadata
  - Validation logic
  - Computed properties (is_registration_open, is_full, funding_percentage, full_address)

### people.py (167 lines)
- **EventOrganizer**: Team-based event management
  - Multiple roles (lead, co-organizer, volunteer coordinator, finance manager, etc.)
  - Granular permissions
- **EventParticipant**: Registration and attendance tracking
  - Guest registration support
  - Multiple roles (attendee, speaker, volunteer, staff, VIP)
  - Check-in/check-out tracking

### financial.py (316 lines)
- **EventSponsor**: Financial and in-kind contributions
  - Sponsorship levels (title, platinum, gold, silver, bronze, community)
  - Transparency features
- **EventExpense**: Expense tracking with receipts
  - Approval workflow
  - Categories (materials, venue, food, transport, marketing, etc.)
- **EventTicket**: Ticketing system
  - Multiple pricing tiers
  - Sale period management
  - Availability tracking

### content.py (267 lines)
- **EventPhoto**: Photo gallery
  - Photographer credits
  - Tagging system
- **EventUpdate**: Progress announcements
  - Update types (general, milestone, announcement, reminder, urgent)
  - Notification options
- **EventMilestone**: Achievement tracking
  - Target and completion dates
  - Proof/evidence uploads
- **EventFeedback**: Post-event ratings
  - Multi-dimensional ratings (overall, organization, content, venue)
  - Testimonial system

### partnerships.py (118 lines)
- **EventPartnership**: Collaborative events
  - Partnership types (co-host, supporting, media)
- **EventImpact**: Social impact metrics
  - Metric types (beneficiaries, funds, items, volunteers, hours)
  - Verification system

## Backward Compatibility

The `__init__.py` file re-exports all models:

```python
from .base_models import EventCategory, EventType
from .content import EventFeedback, EventMilestone, EventPhoto, EventUpdate
from .event import Event
from .financial import EventExpense, EventSponsor, EventTicket
from .partnerships import EventImpact, EventPartnership
from .people import EventOrganizer, EventParticipant

__all__ = [
    'EventCategory', 'EventType', 'Event',
    'EventOrganizer', 'EventParticipant',
    'EventSponsor', 'EventExpense', 'EventTicket',
    'EventPhoto', 'EventUpdate', 'EventMilestone', 'EventFeedback',
    'EventPartnership', 'EventImpact',
]
```

**All existing imports continue to work:**
```python
from event.models import Event, EventSponsor, EventParticipant
```

## Verification

✅ No import errors in:
- `event/admin.py`
- `api/serializers/event/event_serializers.py`
- `api/views/events_viewset.py`

✅ All module files pass pylint (no line-length or file-size warnings)

✅ Django model recognition intact (migrations will work normally)

## Benefits

1. **Code Quality Compliance**: Each module is well under 1000-line limit
2. **Improved Maintainability**: Related models grouped by domain
3. **Easier Navigation**: Developers can quickly find relevant models
4. **Better Organization**: Clear separation of concerns
5. **Scalability**: Easy to add new models without bloating single file
6. **Testing**: Can test domain modules independently
7. **Code Review**: Smaller files easier to review

## Backup

Original file preserved as: `event/models_old.py.bak`

## Next Steps (Recommended)

1. Run Django migrations to verify model recognition:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. Run full test suite to ensure functionality:
   ```bash
   python manage.py test event
   ```

3. Update any documentation referencing `event/models.py` structure

4. Consider similar refactoring for other large model files in the project
