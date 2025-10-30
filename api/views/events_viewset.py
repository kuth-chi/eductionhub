"""
Event Management ViewSets
Complete CRUD operations for event management system
"""

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Sum
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, parsers, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.serializers.event.event_serializers import (
    EventCategorySerializer, EventCreateUpdateSerializer,
    EventDetailSerializer, EventListSerializer, EventTypeSerializer)
from api.serializers.event.financial_serializers import (
    EventExpenseSerializer, EventSponsorSerializer, EventTicketSerializer)
from api.serializers.event.media_serializers import (
    EventFeedbackCreateSerializer, EventFeedbackSerializer,
    EventMilestoneSerializer, EventPhotoSerializer, EventUpdateSerializer)
from api.serializers.event.organizer_serializers import (
    EventImpactSerializer, EventOrganizerSerializer,
    EventPartnershipSerializer)
from api.serializers.event.participant_serializers import (
    EventParticipantCreateSerializer, EventParticipantSerializer)
from event.models import (Event, EventCategory, EventExpense, EventFeedback,
                          EventImpact, EventMilestone, EventOrganizer,
                          EventParticipant, EventPartnership, EventPhoto,
                          EventSponsor, EventTicket, EventType, EventUpdate)
from event.permissions import (EventPermissionChecker,
                               get_user_event_permissions)


class EventCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for event categories (read-only for public)
    """
    queryset = EventCategory.objects.filter(is_active=True)
    serializer_class = EventCategorySerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']


class EventTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for event types (read-only for public)
    """
    queryset = EventType.objects.filter(
        is_active=True).select_related('category')
    serializer_class = EventTypeSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category']
    search_fields = ['name', 'description']


class EventViewSet(viewsets.ModelViewSet):
    """
    ViewSet for events with full CRUD operations
    Permissions:
    - Anyone can view public events
    - Authenticated users can create events
    - Only owner or organizers with edit permission can update/delete
    """
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['event_type', 'status', 'visibility',
                        'country', 'state', 'city', 'is_virtual', 'is_featured']
    search_fields = ['title', 'description', 'tags']
    ordering_fields = ['start_datetime', 'created_at', 'title']
    ordering = ['-start_datetime']

    def get_permissions(self):
        """Define permissions based on action"""
        if self.action in ['list', 'retrieve', 'by_slug']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = Event.objects.select_related(
            'event_type', 'event_type__category',
            'country', 'state', 'city', 'village',
            'target_school', 'target_organization'
        ).prefetch_related(
            'organizers', 'sponsors', 'tickets'
        ).annotate(
            participants_count=Count('participants'),
            sponsors_count=Count('sponsors')
        )

        # Filter by location proximity if lat/lng provided
        latitude = self.request.query_params.get('latitude')
        longitude = self.request.query_params.get('longitude')
        radius_km = self.request.query_params.get('radius_km', 50)

        if latitude and longitude:
            try:
                lat = float(latitude)
                lng = float(longitude)
                radius = float(radius_km)

                # Simple bounding box filter (more efficient than Haversine for initial filtering)
                lat_delta = radius / 111.32
                lng_delta = radius / (111.32 * abs(lat) / 90)

                queryset = queryset.filter(
                    latitude__range=(lat - lat_delta, lat + lat_delta),
                    longitude__range=(lng - lng_delta, lng + lng_delta)
                )
            except (ValueError, TypeError):
                pass

        # Date range filters
        start_from = self.request.query_params.get('start_date_from')
        start_to = self.request.query_params.get('start_date_to')

        if start_from:
            queryset = queryset.filter(start_datetime__gte=start_from)
        if start_to:
            queryset = queryset.filter(start_datetime__lte=start_to)

        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return EventListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return EventCreateUpdateSerializer
        return EventDetailSerializer

    def perform_create(self, serializer):
        """Set creator when creating event"""
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        """Check permissions before updating"""
        event = self.get_object()
        EventPermissionChecker.require_edit_permission(
            self.request.user, event)
        serializer.save()

    def perform_destroy(self, instance):
        """Only owner can delete events"""
        EventPermissionChecker.require_event_owner(self.request.user, instance)
        instance.delete()

    @action(detail=False, methods=['get'], url_path='by-slug/(?P<slug>[-\\w]+)')
    def by_slug(self, request, slug=None):
        """Get event by slug with user permissions"""
        try:
            event = self.get_queryset().get(slug=slug)
            serializer = EventDetailSerializer(event)
            data = serializer.data

            # Add user permissions if authenticated
            if request.user.is_authenticated:
                data['user_permissions'] = get_user_event_permissions(
                    request.user, event
                )

            return Response(data)
        except ObjectDoesNotExist:
            return Response(
                {'error': 'Event not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def management_dashboard(self, request, pk=None):  # pylint: disable=unused-argument
        """Get comprehensive management dashboard for event organizers"""
        event = self.get_object()
        EventPermissionChecker.require_edit_permission(request.user, event)

        # Get statistics
        participants = event.participants.all()
        sponsors = event.sponsors.all()
        expenses = event.expenses.all()

        dashboard_data = {
            'event': EventDetailSerializer(event).data,
            'user_permissions': get_user_event_permissions(request.user, event),
            'statistics': {
                'total_participants': participants.count(),
                'confirmed_participants': participants.filter(status='confirmed').count(),
                'attended_participants': participants.filter(status='attended').count(),
                'waitlist_count': participants.filter(status='waitlist').count(),
                'total_sponsors': sponsors.count(),
                'total_sponsorship': sponsors.aggregate(
                    total=Sum('contribution_amount')
                )['total'] or 0,
                'total_expenses': expenses.filter(status='approved').aggregate(
                    total=Sum('amount')
                )['total'] or 0,
                'pending_expenses': expenses.filter(status='pending').count(),
            },
            'recent_participants': EventParticipantSerializer(
                participants.order_by('-registration_date')[:10], many=True
            ).data,
            'organizers': EventOrganizerSerializer(
                event.organizers.all(), many=True
            ).data,
        }

        return Response(dashboard_data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def publish(self, request, pk=None):  # pylint: disable=unused-argument
        """Publish a draft event"""
        event = self.get_object()
        EventPermissionChecker.require_edit_permission(request.user, event)

        if event.status != 'draft':
            return Response(
                {'error': 'Only draft events can be published'},
                status=status.HTTP_400_BAD_REQUEST
            )

        event.status = 'published'
        event.published_at = timezone.now()
        event.save()

        return Response({
            'message': 'Event published successfully',
            'event': EventDetailSerializer(event).data
        })

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def cancel(self, request, pk=None):  # pylint: disable=unused-argument
        """Cancel an event"""
        event = self.get_object()
        EventPermissionChecker.require_event_owner(request.user, event)

        event.status = 'cancelled'
        event.save()

        return Response({
            'message': 'Event cancelled successfully',
            'event': EventDetailSerializer(event).data
        })

    @action(detail=True, methods=['get'])
    def participants_list(self, request, pk=None):  # pylint: disable=unused-argument
        """Get list of participants (public or full based on permissions)"""
        event = self.get_object()

        # Check if user can see full participant details
        can_manage = EventPermissionChecker.can_manage_participants(
            request.user, event
        )

        participants = event.participants.all()

        if can_manage:
            serializer = EventParticipantSerializer(participants, many=True)
        else:
            # Public view - limited info
            participants = participants.filter(
                status__in=['confirmed', 'attended'])
            serializer = EventParticipantSerializer(participants, many=True)
            # Filter sensitive data
            data = serializer.data
            for item in data:
                item.pop('email', None)
                item.pop('phone', None)
                item.pop('special_requirements', None)
                item.pop('notes', None)

        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_events(self, request):
        """Get events where user is owner or organizer"""
        # Events created by user
        owned_events = Event.objects.filter(created_by=request.user)

        # Events where user is organizer
        organizer_records = EventOrganizer.objects.filter(user=request.user)
        organized_event_ids = organizer_records.values_list(
            'event_id', flat=True)
        organized_events = Event.objects.filter(id__in=organized_event_ids)

        # Combine and deduplicate
        all_events = (owned_events | organized_events).distinct().order_by(
            '-start_datetime')

        serializer = EventListSerializer(
            all_events, many=True, context={'request': request})
        return Response(serializer.data)


class EventParticipantViewSet(viewsets.ModelViewSet):
    """
    ViewSet for event participants and registrations
    Permissions:
    - Anyone can register (create) for public events
    - Only authenticated users can view their own registrations
    - Only organizers can view all participants and manage them
    """
    queryset = EventParticipant.objects.select_related('event', 'user')
    serializer_class = EventParticipantSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['event', 'status', 'role']
    ordering = ['-registration_date']

    def get_permissions(self):
        """Define permissions based on action"""
        if self.action in ['create', 'register']:
            # Anyone can register for events
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """Filter based on user permissions"""
        user = self.request.user
        queryset = super().get_queryset()

        # If user is not authenticated, return empty queryset
        if not user.is_authenticated:
            return queryset.none()

        # If filtering by event, check permissions
        event_id = self.request.query_params.get('event')
        if event_id:
            try:
                event = Event.objects.get(id=event_id)
                # Organizers can see all participants
                if EventPermissionChecker.can_manage_participants(user, event):
                    return queryset.filter(event_id=event_id)
                # Regular users can only see their own registrations
                return queryset.filter(event_id=event_id, user=user)
            except ObjectDoesNotExist:
                return queryset.none()

        # Show only user's own registrations
        return queryset.filter(user=user)

    def get_serializer_class(self):
        if self.action in ['create', 'register']:
            return EventParticipantCreateSerializer
        return EventParticipantSerializer

    def perform_create(self, serializer):
        """Handle registration with auto-linking user if authenticated"""
        validated_data = serializer.validated_data

        # Link user if authenticated
        if self.request.user.is_authenticated:
            validated_data['user'] = self.request.user
            # Auto-fill name if not provided
            if not validated_data.get('name'):
                validated_data['name'] = (
                    self.request.user.get_full_name() or self.request.user.email
                )
            if not validated_data.get('email'):
                validated_data['email'] = self.request.user.email

        serializer.save()

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """Public registration endpoint for visitors/guests"""
        serializer = EventParticipantCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        participant = serializer.save()

        # Return success message
        return Response({
            'message': 'Registration successful',
            'participant': EventParticipantSerializer(participant).data
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_registrations(self, request):
        """Get current user's event registrations"""
        participants = self.queryset.filter(user=request.user)
        serializer = self.get_serializer(participants, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def check_in(self, request, pk=None):  # pylint: disable=unused-argument
        """Check in a participant"""
        participant = self.get_object()
        event = participant.event

        # Check permissions
        EventPermissionChecker.require_participant_management(
            request.user, event)

        participant.check_in_time = timezone.now()
        participant.status = 'attended'
        participant.save()

        serializer = self.get_serializer(participant)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def check_out(self, request, pk=None):  # pylint: disable=unused-argument
        """Check out a participant"""
        participant = self.get_object()
        event = participant.event

        # Check permissions
        EventPermissionChecker.require_participant_management(
            request.user, event)

        participant.check_out_time = timezone.now()
        participant.save()

        serializer = self.get_serializer(participant)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def confirm(self, request, pk=None):  # pylint: disable=unused-argument
        """Confirm a registration (for events requiring approval)"""
        participant = self.get_object()
        event = participant.event

        # Check permissions
        EventPermissionChecker.require_participant_management(
            request.user, event)

        participant.registration_confirmed = True
        participant.status = 'confirmed'
        participant.confirmation_date = timezone.now()
        participant.save()

        # Send confirmation email notification
        # Note: Implement email notification service (e.g., via celery tasks or signals)
        # send_confirmation_email.delay(participant.id)

        serializer = self.get_serializer(participant)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def reject(self, request, pk=None):  # pylint: disable=unused-argument
        """Reject a registration (for events requiring approval)"""
        participant = self.get_object()
        event = participant.event

        # Check permissions
        EventPermissionChecker.require_participant_management(
            request.user, event)

        participant.status = 'cancelled'
        participant.notes = request.data.get(
            'reason', 'Registration rejected by organizer')
        participant.save()

        # Note: Implement notification service to send rejection emails
        # send_rejection_email.delay(participant.id)

        serializer = self.get_serializer(participant)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):  # pylint: disable=unused-argument
        """Cancel a registration (user can cancel their own)"""
        participant = self.get_object()

        # Users can only cancel their own registrations unless they're organizers
        if participant.user != request.user:
            event = participant.event
            EventPermissionChecker.require_participant_management(
                request.user, event)

        participant.status = 'cancelled'
        participant.save()

        serializer = self.get_serializer(participant)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def bulk_check_in(self, request):
        """Bulk check-in participants"""
        event_id = request.data.get('event')
        participant_ids = request.data.get('participant_ids', [])

        try:
            event = Event.objects.get(id=event_id)
        except ObjectDoesNotExist:
            return Response(
                {'error': 'Event not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check permissions
        EventPermissionChecker.require_participant_management(
            request.user, event)

        # Update participants
        updated_count = EventParticipant.objects.filter(
            id__in=participant_ids,
            event=event
        ).update(
            status='attended',
            check_in_time=timezone.now()
        )

        return Response({
            'message': f'Successfully checked in {updated_count} participants'
        })


class EventSponsorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for event sponsors
    Permissions:
    - Anyone can view public sponsors
    - Sponsors/Organizations can register themselves
    - Only organizers with finance permission can manage all sponsors
    """
    queryset = EventSponsor.objects.select_related('event', 'organization')
    serializer_class = EventSponsorSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['event', 'sponsor_type', 'is_public']
    ordering = ['display_order', '-contributed_at']

    def get_permissions(self):
        """Define permissions based on action"""
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        elif self.action == 'register_as_sponsor':
            # Allow any authenticated user or organization to register as sponsor
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """Filter public sponsors or all if user is organizer"""
        queryset = super().get_queryset()
        user = self.request.user

        # If not authenticated, show only public sponsors
        if not user.is_authenticated:
            return queryset.filter(is_public=True)

        # If filtering by event, check permissions
        event_id = self.request.query_params.get('event')
        if event_id:
            try:
                event = Event.objects.get(id=event_id)
                # Organizers with finance permission can see all sponsors
                if EventPermissionChecker.can_manage_finances(user, event):
                    return queryset.filter(event_id=event_id)
                # Others see only public sponsors
                return queryset.filter(event_id=event_id, is_public=True)
            except ObjectDoesNotExist:
                return queryset.none()

        # Show only public sponsors by default
        return queryset.filter(is_public=True)

    def _check_financial_permission(self, event_id):
        """Check if user has permission to manage finances for an event"""
        if not self.request.user.is_authenticated:
            raise PermissionDenied("Authentication required")

        try:
            event = Event.objects.get(id=event_id)
        except ObjectDoesNotExist as exc:
            raise PermissionDenied("Event not found") from exc

        EventPermissionChecker.require_finance_management(
            self.request.user, event)

    def create(self, request, *args, **kwargs):
        """Create sponsor - requires financial permission"""
        event_id = request.data.get('event')
        if event_id:
            self._check_financial_permission(event_id)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Update sponsor - requires financial permission"""
        sponsor = self.get_object()
        self._check_financial_permission(sponsor.event_id)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Delete sponsor - requires financial permission"""
        sponsor = self.get_object()
        self._check_financial_permission(sponsor.event_id)
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def register_as_sponsor(self, request):
        """
        Allow organizations or individuals to register as sponsors
        Sponsors can submit their sponsorship details for approval
        """
        event_id = request.data.get('event')

        try:
            event = Event.objects.get(id=event_id)
        except ObjectDoesNotExist:
            return Response(
                {'error': 'Event not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if registration is open
        if event.status not in ['published', 'ongoing']:
            return Response(
                {'error': 'Sponsorship registration is not open for this event'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Prepare sponsor data
        sponsor_data = request.data.copy()

        # Check if user has an organization
        organization_id = sponsor_data.get('organization')
        if not organization_id:
            # Allow individual sponsorship
            sponsor_data['sponsor_name'] = request.user.get_full_name(
            ) or request.user.email

        # Set default visibility to false (requires approval)
        if 'is_public' not in sponsor_data:
            sponsor_data['is_public'] = False

        # Create sponsor
        serializer = self.get_serializer(data=sponsor_data)
        serializer.is_valid(raise_exception=True)
        sponsor = serializer.save()

        # Send notification to event organizers about new sponsor registration
        # Note: Implement via celery tasks or signal handlers to notify organizers
        # Example: send_sponsor_notification.delay(sponsor.id)

        return Response({
            'message': 'Sponsorship registration submitted successfully. '
                       'Event organizers will review your submission.',
            'sponsor': EventSponsorSerializer(sponsor).data
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def approve(self, request, pk=None):  # pylint: disable=unused-argument
        """Approve a sponsor (make public)"""
        sponsor = self.get_object()
        self._check_financial_permission(sponsor.event_id)

        sponsor.is_public = True
        sponsor.save()

        # Note: Implement notification service to send approval emails
        # This could use celery tasks or signal handlers to notify the sponsor

        serializer = self.get_serializer(sponsor)
        return Response({
            'message': 'Sponsor approved successfully',
            'sponsor': serializer.data
        })

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def reject(self, request, pk=None):  # pylint: disable=unused-argument
        """Reject a sponsor registration"""
        sponsor = self.get_object()
        self._check_financial_permission(sponsor.event_id)

        # Delete the sponsor registration
        sponsor.delete()

        return Response({
            'message': 'Sponsor registration rejected'
        }, status=status.HTTP_204_NO_CONTENT)


class EventExpenseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for event expenses with approval workflow
    Permissions:
    - Only organizers with finance permission can view/manage expenses
    """
    queryset = EventExpense.objects.select_related(
        'event', 'submitted_by', 'approved_by')
    serializer_class = EventExpenseSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [
        parsers.JSONParser,
        parsers.MultiPartParser,
        parsers.FormParser
    ]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['event', 'category', 'status']
    ordering = ['-expense_date']

    def get_queryset(self):
        """Filter based on finance management permissions"""
        user = self.request.user
        queryset = super().get_queryset()

        # If filtering by event, check permissions
        event_id = self.request.query_params.get('event')
        if event_id:
            try:
                event = Event.objects.get(id=event_id)
                EventPermissionChecker.require_finance_management(user, event)
                return queryset.filter(event_id=event_id)
            except ObjectDoesNotExist:
                return queryset.none()

        # Show expenses for events user can manage finances for
        # Get events where user is owner
        owned_events = Event.objects.filter(created_by=user)

        # Get events where user is finance organizer
        finance_organizer_events = EventOrganizer.objects.filter(
            user=user,
            can_manage_finances=True
        ).values_list('event_id', flat=True)

        all_event_ids = list(owned_events.values_list(
            'id', flat=True)) + list(finance_organizer_events)
        return queryset.filter(event_id__in=all_event_ids)

    def perform_create(self, serializer):
        """Check permissions and set submitter"""
        event = serializer.validated_data['event']
        EventPermissionChecker.require_finance_management(
            self.request.user, event)
        serializer.save(submitted_by=self.request.user)

    def perform_update(self, serializer):
        """Check permissions before updating"""
        expense = self.get_object()
        EventPermissionChecker.require_finance_management(
            self.request.user, expense.event
        )
        serializer.save()

    def perform_destroy(self, instance):
        """Check permissions before deleting"""
        EventPermissionChecker.require_finance_management(
            self.request.user, instance.event
        )
        instance.delete()

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):  # pylint: disable=unused-argument
        """Approve an expense"""
        expense = self.get_object()
        EventPermissionChecker.require_finance_management(
            request.user, expense.event
        )

        expense.status = 'approved'
        expense.approved_by = request.user
        expense.approved_at = timezone.now()
        expense.notes = request.data.get('notes', expense.notes)
        expense.save()

        serializer = self.get_serializer(expense)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):  # pylint: disable=unused-argument
        """Reject an expense"""
        expense = self.get_object()
        EventPermissionChecker.require_finance_management(
            request.user, expense.event
        )

        expense.status = 'rejected'
        expense.rejection_reason = request.data.get('reason', '')
        expense.save()

        serializer = self.get_serializer(expense)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):  # pylint: disable=unused-argument
        """Mark an expense as paid"""
        expense = self.get_object()
        EventPermissionChecker.require_finance_management(
            request.user, expense.event
        )

        if expense.status != 'approved':
            return Response(
                {'error': 'Only approved expenses can be marked as paid'},
                status=status.HTTP_400_BAD_REQUEST
            )

        expense.status = 'paid'
        expense.payment_date = request.data.get(
            'payment_date', timezone.now().date())
        expense.save()

        serializer = self.get_serializer(expense)
        return Response(serializer.data)


class EventTicketViewSet(viewsets.ModelViewSet):
    """ViewSet for event tickets"""
    queryset = EventTicket.objects.select_related('event')
    serializer_class = EventTicketSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['event', 'is_active']
    ordering = ['display_order', 'price']


class EventPhotoViewSet(viewsets.ModelViewSet):
    """
    ViewSet for event photos
    Permissions:
    - Anyone can view public photos
    - Only organizers with media permission can upload
    """
    queryset = EventPhoto.objects.select_related('event', 'photographer')
    serializer_class = EventPhotoSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['event', 'is_featured', 'is_public']
    ordering = ['display_order', '-uploaded_at']

    def get_permissions(self):
        """Define permissions based on action"""
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """Filter based on visibility and permissions"""
        queryset = super().get_queryset()
        user = self.request.user

        # If not authenticated, show only public photos
        if not user.is_authenticated:
            return queryset.filter(is_public=True)

        # If filtering by event, check permissions
        event_id = self.request.query_params.get('event')
        if event_id:
            try:
                event = Event.objects.get(id=event_id)
                # Organizers can see all photos
                if EventPermissionChecker.can_upload_media(user, event):
                    return queryset.filter(event_id=event_id)
                # Others see only public photos
                return queryset.filter(event_id=event_id, is_public=True)
            except ObjectDoesNotExist:
                return queryset.none()

        # Show only public photos by default
        return queryset.filter(is_public=True)

    def perform_create(self, serializer):
        """Check permissions before uploading"""
        event = serializer.validated_data['event']
        EventPermissionChecker.require_media_upload(self.request.user, event)
        serializer.save(photographer=self.request.user)

    def perform_update(self, serializer):
        """Check permissions before updating"""
        photo = self.get_object()
        EventPermissionChecker.require_media_upload(
            self.request.user, photo.event)
        serializer.save()

    def perform_destroy(self, instance):
        """Check permissions before deleting"""
        EventPermissionChecker.require_media_upload(
            self.request.user, instance.event)
        instance.delete()


class EventUpdateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for event updates and announcements
    Permissions:
    - Anyone can view public updates
    - Only organizers with update posting permission can create/manage
    """
    queryset = EventUpdate.objects.select_related('event', 'posted_by')
    serializer_class = EventUpdateSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['event', 'update_type', 'is_pinned', 'is_public']
    ordering = ['-is_pinned', '-posted_at']

    def get_permissions(self):
        """Define permissions based on action"""
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """Filter based on visibility and permissions"""
        queryset = super().get_queryset()
        user = self.request.user

        # If not authenticated, show only public updates
        if not user.is_authenticated:
            return queryset.filter(is_public=True)

        # If filtering by event, check permissions
        event_id = self.request.query_params.get('event')
        if event_id:
            try:
                event = Event.objects.get(id=event_id)
                # Organizers can see all updates
                if EventPermissionChecker.can_post_updates(user, event):
                    return queryset.filter(event_id=event_id)
                # Others see only public updates
                return queryset.filter(event_id=event_id, is_public=True)
            except ObjectDoesNotExist:
                return queryset.none()

        # Show only public updates by default
        return queryset.filter(is_public=True)

    def perform_create(self, serializer):
        """Check permissions before posting"""
        event = serializer.validated_data['event']
        EventPermissionChecker.require_update_posting(self.request.user, event)
        serializer.save(posted_by=self.request.user)

    def perform_update(self, serializer):
        """Check permissions before updating"""
        update = self.get_object()
        EventPermissionChecker.require_update_posting(
            self.request.user, update.event)
        serializer.save()

    def perform_destroy(self, instance):
        """Check permissions before deleting"""
        EventPermissionChecker.require_update_posting(
            self.request.user, instance.event)
        instance.delete()


class EventMilestoneViewSet(viewsets.ModelViewSet):
    """
    ViewSet for event milestones
    Permissions:
    - Anyone can view public milestones
    - Only organizers with edit permission can manage milestones
    """
    queryset = EventMilestone.objects.select_related('event')
    serializer_class = EventMilestoneSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['event', 'is_completed']
    ordering = ['display_order', 'target_date']

    def get_permissions(self):
        """Define permissions based on action"""
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        """Check permissions before creating"""
        event = serializer.validated_data['event']
        EventPermissionChecker.require_edit_permission(
            self.request.user, event)
        serializer.save()

    def perform_update(self, serializer):
        """Check permissions before updating"""
        milestone = self.get_object()
        EventPermissionChecker.require_edit_permission(
            self.request.user, milestone.event)
        serializer.save()

    def perform_destroy(self, instance):
        """Check permissions before deleting"""
        EventPermissionChecker.require_edit_permission(
            self.request.user, instance.event)
        instance.delete()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def complete(self, request, pk=None):  # pylint: disable=unused-argument
        """Mark milestone as completed"""
        milestone = self.get_object()
        EventPermissionChecker.require_edit_permission(
            request.user, milestone.event)

        milestone.is_completed = True
        milestone.completion_date = timezone.now()
        milestone.completion_notes = request.data.get('completion_notes', '')
        milestone.save()

        serializer = self.get_serializer(milestone)
        return Response(serializer.data)


class EventFeedbackViewSet(viewsets.ModelViewSet):
    """ViewSet for event feedback and ratings"""
    queryset = EventFeedback.objects.select_related('event', 'participant')
    serializer_class = EventFeedbackSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['event', 'is_public', 'is_featured']
    ordering = ['-submitted_at']

    def get_permissions(self):
        """Define permissions based on action"""
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        """Use create serializer for POST requests"""
        if self.action == 'create':
            from api.serializers.event.media_serializers import \
                EventFeedbackCreateSerializer
            return EventFeedbackCreateSerializer
        return EventFeedbackSerializer

    def get_queryset(self):
        """Filter based on visibility"""
        queryset = super().get_queryset()
        user = self.request.user

        # If not authenticated, show only public feedback
        if not user.is_authenticated:
            return queryset.filter(is_public=True)

        # If filtering by event
        event_id = self.request.query_params.get('event')
        if event_id:
            # Show all feedback for the event (public for guests, all for participants/organizers)
            return queryset.filter(event_id=event_id)

        # Show only public feedback by default
        return queryset.filter(is_public=True)


class EventOrganizerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for event organizers
    Permissions:
    - Only authenticated users can view organizers
    - Only event owner or lead organizers can add/remove organizers
    - Only event owner or lead organizers can update permissions
    """
    queryset = EventOrganizer.objects.select_related('event', 'user')
    serializer_class = EventOrganizerSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['event', 'role']
    ordering = ['-added_at']

    def get_queryset(self):
        """Filter to show only user's organized events or event-specific organizers"""
        user = self.request.user
        queryset = super().get_queryset()

        # If filtering by event, check if user can view that event's organizers
        event_id = self.request.query_params.get('event')
        if event_id:
            try:
                event = Event.objects.get(id=event_id)
                # Check if user is owner or organizer of this event
                if not (EventPermissionChecker.is_event_owner(user, event) or
                        EventPermissionChecker.is_organizer(user, event)):
                    raise PermissionDenied(
                        "You are not authorized to view organizers of this event"
                    )
                return queryset.filter(event_id=event_id)
            except ObjectDoesNotExist:
                return queryset.none()

        # Show all events where user is an organizer or owner
        user_events = Event.objects.filter(created_by=user)
        organizer_events = queryset.filter(
            user=user).values_list('event_id', flat=True)
        all_event_ids = list(user_events.values_list(
            'id', flat=True)) + list(organizer_events)

        return queryset.filter(event_id__in=all_event_ids)

    def perform_create(self, serializer):
        """Check permissions before adding organizer"""
        event = serializer.validated_data['event']
        EventPermissionChecker.require_organizer_management(
            self.request.user, event)
        serializer.save()

    def perform_update(self, serializer):
        """Check permissions before updating organizer"""
        organizer = self.get_object()
        EventPermissionChecker.require_organizer_management(
            self.request.user, organizer.event
        )
        serializer.save()

    def perform_destroy(self, instance):
        """Check permissions and prevent removing last lead organizer"""
        event = instance.event
        EventPermissionChecker.require_organizer_management(
            self.request.user, event)

        # Don't allow removing the last lead organizer
        if instance.role == 'lead':
            lead_count = EventOrganizer.objects.filter(
                event=event,
                role='lead'
            ).count()
            if lead_count <= 1:
                raise PermissionDenied(
                    'Cannot remove the last lead organizer'
                )

        instance.delete()

    @action(detail=False, methods=['get'])
    def my_events(self, request):
        """Get all events where current user is an organizer"""
        user = request.user

        organizer_event_ids = set(
            EventOrganizer.objects.filter(
                user=user).values_list('event_id', flat=True)
        )
        owner_event_ids = set(
            Event.objects.filter(created_by=user).values_list('id', flat=True)
        )
        all_event_ids = organizer_event_ids | owner_event_ids

        if not all_event_ids:
            return Response([])

        events = Event.objects.filter(id__in=all_event_ids).select_related(
            'event_type', 'event_type__category', 'country', 'state', 'city'
        ).order_by('-start_datetime')

        serialized_events = EventListSerializer(
            events, many=True, context={'request': request}
        ).data

        enriched_events = []
        for event_obj, serialized in zip(events, serialized_events):
            event_data = dict(serialized)
            permissions = get_user_event_permissions(user, event_obj) or {}
            event_data['user_permissions'] = permissions
            event_data['user_role'] = permissions.get('role')
            enriched_events.append(event_data)

        return Response(enriched_events)

    @action(detail=True, methods=['patch'])
    def update_permissions(self, request, pk=None):  # pylint: disable=unused-argument
        """Update organizer permissions (only owner or lead)"""
        organizer = self.get_object()
        event = organizer.event

        EventPermissionChecker.require_organizer_management(
            request.user, event)

        # Update permissions
        permissions = ['can_edit_event', 'can_manage_participants', 'can_manage_finances',
                       'can_upload_media', 'can_post_updates']
        for perm in permissions:
            if perm in request.data:
                setattr(organizer, perm, request.data[perm])

        # Allow updating role if provided
        if 'role' in request.data:
            organizer.role = request.data['role']

        organizer.save()
        serializer = self.get_serializer(organizer)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def invite_organizer(self, request):
        """Invite a user to be an organizer (by email or user ID)"""
        event_id = request.data.get('event')
        try:
            event = Event.objects.get(id=event_id)
        except ObjectDoesNotExist:
            return Response(
                {'error': 'Event not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        EventPermissionChecker.require_organizer_management(
            request.user, event)

        # Check if user_id or email is provided
        user_id = request.data.get('user')
        if not user_id:
            return Response(
                {'error': 'User ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user is already an organizer
        if EventOrganizer.objects.filter(event=event, user_id=user_id).exists():
            return Response(
                {'error': 'User is already an organizer of this event'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create organizer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Send invitation notification to user
        # Note: Implement notification service to send invitation emails
        # This could use celery tasks or signal handlers to notify the invited user

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class EventPartnershipViewSet(viewsets.ModelViewSet):
    """ViewSet for event partnerships"""
    queryset = EventPartnership.objects.select_related(
        'event', 'partner_organization')
    serializer_class = EventPartnershipSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['event', 'is_public']
    ordering = ['display_order', '-created_at']


class EventImpactViewSet(viewsets.ModelViewSet):
    """ViewSet for event impact metrics"""
    queryset = EventImpact.objects.select_related('event')
    serializer_class = EventImpactSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['event', 'metric_type', 'verified']
    ordering = ['display_order', '-created_at']
