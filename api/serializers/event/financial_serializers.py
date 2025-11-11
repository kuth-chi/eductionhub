"""Financial and sponsorship serializers"""

from django.utils import timezone
from rest_framework import serializers

from event.models import EventExpense, EventSponsor, EventTicket


class EventSponsorSerializer(serializers.ModelSerializer):
    """Event sponsor details"""
    organization_name = serializers.CharField(
        source='organization.name',
        read_only=True
    )

    class Meta:
        """Meta information for the EventSponsorSerializer"""
        model = EventSponsor
        fields = [
            'id', 'event', 'organization', 'organization_name',
            'sponsor_name', 'sponsor_logo', 'sponsor_website',
            'sponsor_type', 'contribution_amount', 'contribution_description',
            'is_public', 'display_order', 'contributed_at', 'notes'
        ]
        read_only_fields = ['contributed_at']

    def to_representation(self, instance):
        """Hide contribution amount if not public"""
        data = super().to_representation(instance)
        if not instance.is_public and not self.context.get('is_organizer'):
            data.pop('contribution_amount', None)
            data.pop('notes', None)
        return data


class EventExpenseSerializer(serializers.ModelSerializer):
    """Event expense tracking for transparency"""
    submitted_by_name = serializers.CharField(
        source='submitted_by.get_full_name',
        read_only=True
    )
    approved_by_name = serializers.CharField(
        source='approved_by.get_full_name',
        read_only=True
    )

    class Meta:
        """Meta information for the EventExpenseSerializer"""
        model = EventExpense
        fields = [
            'id', 'event', 'category', 'title', 'description',
            'amount', 'currency', 'receipt', 'receipt_number',
            'vendor_name', 'expense_date', 'payment_date',
            'status', 'submitted_by', 'submitted_by_name',
            'approved_by', 'approved_by_name', 'approved_at',
            'notes', 'rejection_reason', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'submitted_by', 'approved_by', 'approved_at',
            'created_at', 'updated_at'
        ]

    def create(self, validated_data):
        """Set submitted_by to current user"""
        validated_data['submitted_by'] = self.context['request'].user
        return super().create(validated_data)


class EventExpenseApprovalSerializer(serializers.Serializer):
    """Approve or reject expense"""
    expense_id = serializers.IntegerField()
    approve = serializers.BooleanField()
    rejection_reason = serializers.CharField(
        required=False,
        allow_blank=True
    )

    def validate(self, attrs):
        """Validate rejection requires reason"""
        if not attrs['approve'] and not attrs.get('rejection_reason'):
            raise serializers.ValidationError(
                'Rejection reason is required when rejecting an expense'
            )
        return attrs

    def create(self, validated_data):
        """Update expense status (approval action)"""

        expense = EventExpense.objects.get(
            id=validated_data['expense_id']
        )

        if validated_data['approve']:
            expense.status = 'approved'
            expense.approved_at = timezone.now()
            expense.approved_by = self.context['request'].user
        else:
            expense.status = 'rejected'
            expense.rejection_reason = validated_data.get(
                'rejection_reason', '')

        expense.save()
        return expense

    def update(self, instance, validated_data):
        """Not implemented - use create for approval actions"""
        raise NotImplementedError(
            'Use create() for expense approval/rejection actions'
        )


class EventTicketSerializer(serializers.ModelSerializer):
    """Event ticket types"""
    is_available = serializers.BooleanField(read_only=True)
    remaining = serializers.SerializerMethodField()

    class Meta:
        """Meta information for the EventTicketSerializer"""
        model = EventTicket
        fields = [
            'id', 'event', 'name', 'description', 'price', 'currency',
            'quantity', 'quantity_sold', 'remaining',
            'sale_start', 'sale_end', 'status', 'is_available',
            'display_order', 'max_per_order'
        ]

    def get_remaining(self, obj):
        """Calculate remaining tickets"""
        if obj.quantity is None:
            return None
        return max(0, obj.quantity - obj.quantity_sold)


class EventFinancialSummarySerializer(serializers.Serializer):
    """Financial summary for an event"""
    total_funding = serializers.DecimalField(max_digits=12, decimal_places=2)
    funding_goal = serializers.DecimalField(max_digits=12, decimal_places=2)
    funding_percentage = serializers.FloatField()
    total_expenses = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_approved_expenses = serializers.DecimalField(
        max_digits=12, decimal_places=2)
    remaining_budget = serializers.DecimalField(
        max_digits=12, decimal_places=2)
    sponsors_count = serializers.IntegerField()
    expenses_count = serializers.IntegerField()
    currency = serializers.CharField()

    def create(self, validated_data):
        """Not implemented - summary is read-only"""
        raise NotImplementedError(
            'EventFinancialSummarySerializer is read-only'
        )

    def update(self, instance, validated_data):
        """Not implemented - summary is read-only"""
        raise NotImplementedError(
            'EventFinancialSummarySerializer is read-only'
        )
