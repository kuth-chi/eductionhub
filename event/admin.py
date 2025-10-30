"""
Admin interface for event management
"""

from django.contrib import admin
from django.utils.html import format_html

from .models import (Event, EventCategory, EventExpense, EventFeedback,
                     EventImpact, EventMilestone, EventOrganizer,
                     EventParticipant, EventPartnership, EventPhoto,
                     EventSponsor, EventTicket, EventType, EventUpdate)


@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    """Admin for event categories"""
    list_display = ['name', 'slug',
                    'parent_category', 'is_active', 'created_at']
    list_filter = ['is_active', 'parent_category']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    """Admin for event types"""
    list_display = ['name', 'category', 'slug', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}


class EventOrganizerInline(admin.TabularInline):
    """Inline for event organizers"""
    model = EventOrganizer
    extra = 1
    fk_name = 'event'
    fields = ['user', 'role', 'can_edit_event', 'can_manage_participants']


class EventSponsorInline(admin.TabularInline):
    """Inline for event sponsors"""
    model = EventSponsor
    extra = 1
    fk_name = 'event'
    fields = ['sponsor_name', 'sponsor_type',
              'contribution_amount', 'is_public']


class EventTicketInline(admin.TabularInline):
    """Inline for event tickets"""
    model = EventTicket
    extra = 1
    fk_name = 'event'
    fields = ['name', 'price', 'quantity',
              'quantity_sold', 'status']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """Admin for events"""
    list_display = [
        'title', 'event_type', 'status', 'visibility', 'location_info',
        'start_datetime', 'participants_count', 'is_featured'
    ]
    list_filter = [
        'status', 'visibility', 'event_type', 'is_featured', 'is_virtual',
        'country', 'start_datetime'
    ]
    search_fields = ['title', 'description', 'location_name', 'tags']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['created_by', 'target_school', 'target_organization']
    readonly_fields = ['uuid', 'created_at',
                       'updated_at', 'funding_percentage_display']

    fieldsets = (
        ('Basic Info', {
            'fields': (
                'title', 'slug', 'event_type', 'description', 'short_description', 'tags'
            )
        }),
        ('Target & Scope', {
            'fields': ('target_school', 'target_organization')
        }),
        ('Location - Administrative', {
            'fields': ('country', 'state', 'city', 'village'),
            'description': 'Select from existing geographic hierarchy'
        }),
        ('Location - Precise (Lat/Lon)', {
            'fields': (
                'latitude', 'longitude', 'location_name', 'address_line_1',
                'address_line_2', 'postal_code', 'location_instructions',
                'google_maps_url'
            ),
            'description': (
                'Exact coordinates for maps and mobile location. '
                'Use Google Maps to find coordinates.'
            )
        }),
        ('Virtual Event', {
            'fields': ('is_virtual', 'virtual_meeting_url', 'virtual_meeting_password'),
            'classes': ('collapse',)
        }),
        ('Schedule', {
            'fields': (
                'start_datetime', 'end_datetime', 'timezone',
                'registration_start', 'registration_deadline', 'max_participants'
            )
        }),
        ('Media', {
            'fields': ('banner_image', 'thumbnail_image', 'video_url')
        }),
        ('Financial', {
            'fields': ('funding_goal', 'current_funding', 'currency', 'funding_percentage_display'),
            'classes': ('collapse',)
        }),
        ('Status & Visibility', {
            'fields': ('status', 'visibility', 'requires_approval', 'is_featured')
        }),
        ('SEO', {
            'fields': ('meta_description', 'og_image'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('uuid', 'created_by', 'created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )

    inlines = [EventOrganizerInline, EventSponsorInline, EventTicketInline]

    def location_info(self, obj):
        """Display location information with icons"""
        if obj.country:
            return format_html(
                '<span style="color: orange;">🌍 {}, {}</span>',
                obj.country.name,
                obj.state.name if obj.state else 'N/A'
            )
        if obj.is_virtual:
            return format_html('<span style="color: blue;">🌐 Virtual</span>')
        if obj.latitude and obj.longitude:
            return format_html(
                '<span style="color: green;">📍 {}, {}</span>',
                obj.latitude, obj.longitude
            )
        return obj.location_name or obj.city
    location_info.short_description = 'Location'

    def participants_count(self, obj):
        """Display count of registered participants"""
        count = obj.participants.filter(status='registered').count()
        max_p = obj.max_participants
        if max_p:
            return f"{count}/{max_p}"
        return str(count)
    participants_count.short_description = 'Participants'

    def funding_percentage_display(self, obj):
        """Display funding percentage with progress bar"""
        if obj.funding_goal:
            pct = obj.funding_percentage
            return format_html(
                '<progress value="{}" max="100"></progress> {}%',
                pct, round(pct, 1)
            )
        return '-'
    funding_percentage_display.short_description = 'Funding Progress'


@admin.register(EventOrganizer)
class EventOrganizerAdmin(admin.ModelAdmin):
    """Admin for event organizers"""
    list_display = ['user', 'event', 'role', 'can_edit_event', 'added_at']
    list_filter = ['role', 'can_edit_event', 'can_manage_finances']
    search_fields = ['user__email', 'event__title']
    raw_id_fields = ['event', 'user']


@admin.register(EventSponsor)
class EventSponsorAdmin(admin.ModelAdmin):
    """Admin for event sponsors"""
    list_display = [
        'sponsor_name', 'event', 'sponsor_type', 'contribution_amount',
        'is_public', 'contributed_at'
    ]
    list_filter = ['sponsor_type', 'is_public', 'contributed_at']
    search_fields = ['sponsor_name', 'event__title']
    raw_id_fields = ['event', 'organization']


@admin.register(EventExpense)
class EventExpenseAdmin(admin.ModelAdmin):
    """Admin for event expenses"""
    list_display = [
        'title', 'event', 'category', 'amount', 'status',
        'expense_date', 'submitted_by', 'approved_by'
    ]
    list_filter = ['status', 'category', 'expense_date']
    search_fields = ['title', 'description', 'vendor_name', 'event__title']
    raw_id_fields = ['event', 'submitted_by', 'approved_by']
    readonly_fields = ['created_at', 'updated_at', 'approved_at']

    fieldsets = (
        ('Expense Details', {
            'fields': ('event', 'category', 'title', 'description', 'amount', 'currency')
        }),
        ('Documentation', {
            'fields': ('receipt', 'receipt_number', 'vendor_name', 'expense_date', 'payment_date')
        }),
        ('Approval', {
            'fields': ('status', 'submitted_by', 'approved_by', 'approved_at', 'rejection_reason')
        }),
        ('Additional', {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
    )


@admin.register(EventParticipant)
class EventParticipantAdmin(admin.ModelAdmin):
    """Admin for event participants"""
    list_display = [
        'name', 'email', 'event', 'role', 'status',
        'registration_date', 'check_in_time'
    ]
    list_filter = ['status', 'role',
                   'registration_date', 'registration_confirmed']
    search_fields = ['name', 'email', 'event__title', 'organization_name']
    raw_id_fields = ['event', 'user']
    readonly_fields = ['registration_date']


@admin.register(EventPhoto)
class EventPhotoAdmin(admin.ModelAdmin):
    """Admin for event photos"""
    list_display = [
        'event', 'caption_preview', 'photographer', 'taken_at',
        'is_featured', 'is_public', 'uploaded_at'
    ]
    list_filter = ['is_featured', 'is_public', 'uploaded_at']
    search_fields = ['caption', 'event__title', 'tags']
    raw_id_fields = ['event', 'photographer']

    def caption_preview(self, obj):
        """Display a short preview of the caption"""
        return obj.caption[:50] + '...' if len(obj.caption) > 50 else obj.caption
    caption_preview.short_description = 'Caption'


@admin.register(EventUpdate)
class EventUpdateAdmin(admin.ModelAdmin):
    """Admin for event updates"""
    list_display = [
        'title', 'event', 'update_type', 'posted_by',
        'posted_at', 'is_pinned', 'is_public'
    ]
    list_filter = ['update_type', 'is_pinned', 'is_public', 'posted_at']
    search_fields = ['title', 'content', 'event__title']
    raw_id_fields = ['event', 'posted_by']


@admin.register(EventMilestone)
class EventMilestoneAdmin(admin.ModelAdmin):
    """Admin for event milestones"""
    list_display = [
        'title', 'event', 'target_date', 'completion_date',
        'is_completed', 'display_order'
    ]
    list_filter = ['is_completed', 'target_date']
    search_fields = ['title', 'description', 'event__title']
    raw_id_fields = ['event']


@admin.register(EventFeedback)
class EventFeedbackAdmin(admin.ModelAdmin):
    """Admin for event feedback"""
    list_display = [
        'event', 'participant', 'overall_rating', 'would_recommend',
        'is_public', 'is_featured', 'submitted_at'
    ]
    list_filter = ['overall_rating',
                   'would_recommend', 'is_public', 'is_featured']
    search_fields = ['comment', 'event__title', 'participant__name']
    raw_id_fields = ['event', 'participant']
    readonly_fields = ['submitted_at']


@admin.register(EventTicket)
class EventTicketAdmin(admin.ModelAdmin):
    """Admin for event tickets"""
    list_display = [
        'name', 'event', 'price', 'currency', 'quantity',
        'quantity_sold', 'status', 'availability_status'
    ]
    list_filter = ['status', 'currency']
    search_fields = ['name', 'event__title']
    raw_id_fields = ['event']

    def availability_status(self, obj):
        """Display availability status with icons"""
        if obj.is_available:
            return format_html('<span style="color: green;">✓ Available</span>')
        return format_html('<span style="color: red;">✗ Unavailable</span>')
    availability_status.short_description = 'Availability'


@admin.register(EventPartnership)
class EventPartnershipAdmin(admin.ModelAdmin):
    """Admin for event partnerships"""
    list_display = ['partner_organization',
                    'event', 'partnership_type', 'is_public']
    list_filter = ['partnership_type', 'is_public']
    search_fields = ['event__title', 'partner_organization__name']
    raw_id_fields = ['event', 'partner_organization']


@admin.register(EventImpact)
class EventImpactAdmin(admin.ModelAdmin):
    """Admin for event impact metrics"""
    list_display = [
        'metric_name', 'metric_value', 'metric_unit', 'event',
        'metric_type', 'verified', 'display_order'
    ]
    list_filter = ['metric_type', 'verified']
    search_fields = ['metric_name', 'description', 'event__title']
    raw_id_fields = ['event']
