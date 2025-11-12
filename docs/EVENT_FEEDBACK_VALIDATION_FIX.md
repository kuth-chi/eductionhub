# Event Feedback Validation Fix

## Issue
Event feedback submission was returning a 400 error: "You must be registered for this event to provide feedback" even for users who were legitimate event participants.

## Root Cause
The `EventFeedbackCreateSerializer.create()` method had several issues:

1. **Incorrect query**: Used `event.participants.get()` instead of `EventParticipant.objects.get()`
2. **Broad exception handling**: Caught all exceptions with `except Exception`, masking the real error
3. **Missing duplicate check**: No validation to prevent duplicate feedback submissions before hitting the database unique constraint

## Changes Made

### 1. Fixed Participant Lookup
**File**: `api/serializers/event/media_serializers.py`

**Before**:
```python
try:
    participant = event.participants.get(
        user=user,
        status__in=['registered', 'confirmed', 'attended']
    )
    validated_data['participant'] = participant
except Exception as exc:
    raise serializers.ValidationError(
        'You must be registered for this event to provide feedback'
    ) from exc
```

**After**:
```python
from event.models import EventParticipant

try:
    participant = EventParticipant.objects.get(
        event=event,
        user=user,
        status__in=['registered', 'confirmed', 'attended']
    )
    validated_data['participant'] = participant
except EventParticipant.DoesNotExist as exc:
    raise serializers.ValidationError(
        'You must be registered for this event to provide feedback'
    ) from exc
except EventParticipant.MultipleObjectsReturned:
    # Fallback if multiple records exist (shouldn't happen)
    participant = EventParticipant.objects.filter(
        event=event,
        user=user,
        status__in=['registered', 'confirmed', 'attended']
    ).first()
    if not participant:
        raise serializers.ValidationError(
            'You must be registered for this event to provide feedback'
        )
    validated_data['participant'] = participant
```

### 2. Added Duplicate Feedback Check
Added a `validate()` method to check for existing feedback before attempting to create:

```python
def validate(self, attrs):
    """Validate event and check for existing feedback"""
    user = self.context['request'].user
    event = attrs['event']
    
    # Check if user has already submitted feedback for this event
    from event.models import EventParticipant
    
    participant = EventParticipant.objects.filter(
        event=event,
        user=user,
        status__in=['registered', 'confirmed', 'attended']
    ).first()
    
    if participant and EventFeedback.objects.filter(
        event=event,
        participant=participant
    ).exists():
        raise serializers.ValidationError(
            'You have already submitted feedback for this event'
        )
    
    return attrs
```

## Validation Logic

### Who Can Submit Feedback?
Users can submit feedback if they meet ALL of these criteria:

1. **Authenticated**: Must be logged in with a user account
2. **Registered**: Must have an `EventParticipant` record linked to their user account
3. **Valid Status**: Participant status must be one of:
   - `registered` - Signed up for the event
   - `confirmed` - Registration confirmed by organizers
   - `attended` - Marked as attended the event

### Who CANNOT Submit Feedback?
- **Guest Participants**: Users registered without a user account (`EventParticipant.user = null`)
- **Cancelled Participants**: Users with `status='cancelled'`
- **Waitlisted Participants**: Users with `status='waitlist'`
- **No-Show Participants**: Users with `status='no-show'`
- **Non-Participants**: Users who never registered for the event
- **Duplicate Submitters**: Users who already submitted feedback

## Data Model Context

### EventParticipant Model
```python
class EventParticipant(models.Model):
    event = ForeignKey(Event)
    user = ForeignKey(User, null=True, blank=True)  # Optional for guest registration
    name = CharField(max_length=255)
    email = EmailField()
    status = CharField(choices=PARTICIPANT_STATUS, default='registered')
    # ...
```

### EventFeedback Model
```python
class EventFeedback(models.Model):
    event = ForeignKey(Event)
    participant = ForeignKey(EventParticipant)  # Required
    overall_rating = IntegerField(choices=[(i, i) for i in range(1, 6)])
    # ...
    
    class Meta:
        unique_together = ['event', 'participant']  # One feedback per participant
```

## API Endpoint

**URL**: `POST /api/v1/event-feedback/`

**Required Fields**:
```json
{
  "event": 123,
  "overall_rating": 5,
  "is_public": true
}
```

**Optional Fields**:
```json
{
  "organization_rating": 5,
  "content_rating": 4,
  "venue_rating": 5,
  "comment": "Great event!",
  "what_went_well": "Well organized",
  "what_to_improve": "More food options",
  "would_recommend": true
}
```

**Response Codes**:
- `201 Created` - Feedback submitted successfully
- `400 Bad Request` - Validation error (not registered, already submitted, etc.)
- `401 Unauthorized` - Not authenticated
- `404 Not Found` - Event doesn't exist

## Error Messages

| Error Message | Meaning |
|---------------|---------|
| "You must be registered for this event to provide feedback" | User doesn't have an EventParticipant record with valid status |
| "You have already submitted feedback for this event" | User already submitted feedback (unique constraint) |
| "Authentication credentials were not provided." | User not logged in |

## Testing Scenarios

### ✅ Valid Submission
1. User is authenticated
2. User has `EventParticipant` record with `status='attended'`
3. User hasn't submitted feedback yet
4. Result: Feedback created successfully

### ❌ Invalid: Not Registered
1. User is authenticated
2. User has no `EventParticipant` record for the event
3. Result: 400 "You must be registered for this event to provide feedback"

### ❌ Invalid: Wrong Status
1. User is authenticated
2. User has `EventParticipant` with `status='cancelled'`
3. Result: 400 "You must be registered for this event to provide feedback"

### ❌ Invalid: Duplicate Feedback
1. User is authenticated
2. User has valid `EventParticipant` record
3. User already submitted feedback
4. Result: 400 "You have already submitted feedback for this event"

### ❌ Invalid: Guest Participant
1. User is authenticated
2. Another user registered as guest using authenticated user's email
3. Guest participant has `user=null`
4. Result: 400 "You must be registered for this event to provide feedback"

## Frontend Integration

The frontend should:

1. **Check participant status before showing feedback form**:
```typescript
const canProvideFeedback = participant?.status in ['registered', 'confirmed', 'attended'];
```

2. **Handle error responses gracefully**:
```typescript
try {
  await submitFeedback(data);
  toast.success("Feedback submitted successfully!");
} catch (error) {
  if (error.response?.status === 400) {
    toast.error(error.response.data.non_field_errors?.[0] || "Validation error");
  } else {
    toast.error("Failed to submit feedback");
  }
}
```

3. **Check for existing feedback**:
Query `GET /api/v1/event-feedback/?event={eventId}` and check if current user already submitted.

## Related Files
- `api/serializers/event/media_serializers.py` - Serializer with validation
- `api/views/events_viewset.py` - EventFeedbackViewSet
- `event/models/content.py` - EventFeedback model
- `event/models/people.py` - EventParticipant model

## See Also
- [Event Registration & Tickets Analysis](EVENT_REGISTRATION_TICKETS_ANALYSIS.md)
- Event permissions documentation
- EventParticipant status lifecycle
