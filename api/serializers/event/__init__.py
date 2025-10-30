"""Event management serializers"""

from .event_serializers import (
    EventCategorySerializer,
    EventTypeSerializer,
    EventListSerializer,
    EventDetailSerializer,
    EventCreateUpdateSerializer,
)
from .participant_serializers import (
    EventParticipantSerializer,
    EventParticipantCreateSerializer,
    EventParticipantCheckInSerializer,
)
from .financial_serializers import (
    EventSponsorSerializer,
    EventExpenseSerializer,
    EventTicketSerializer,
)
from .media_serializers import (
    EventPhotoSerializer,
    EventUpdateSerializer,
    EventMilestoneSerializer,
    EventFeedbackSerializer,
)
from .organizer_serializers import (
    EventOrganizerSerializer,
    EventPartnershipSerializer,
    EventImpactSerializer,
)

__all__ = [
    # Core event
    'EventCategorySerializer',
    'EventTypeSerializer',
    'EventListSerializer',
    'EventDetailSerializer',
    'EventCreateUpdateSerializer',
    # Participants
    'EventParticipantSerializer',
    'EventParticipantCreateSerializer',
    'EventParticipantCheckInSerializer',
    # Financial
    'EventSponsorSerializer',
    'EventExpenseSerializer',
    'EventTicketSerializer',
    # Media
    'EventPhotoSerializer',
    'EventUpdateSerializer',
    'EventMilestoneSerializer',
    'EventFeedbackSerializer',
    # Organization
    'EventOrganizerSerializer',
    'EventPartnershipSerializer',
    'EventImpactSerializer',
]
