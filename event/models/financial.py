"""
Financial models: sponsors, expenses, and tickets.
"""
# pylint: disable=no-member

from decimal import Decimal
from django.utils import timezone
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .event import Event


class EventSponsor(models.Model):
    """
    Sponsors and their contributions (financial or in-kind).
    Supports transparency and acknowledgment.
    """
    SPONSOR_TYPE = [
        ('title', _('Title Sponsor')),
        ('platinum', _('Platinum')),
        ('gold', _('Gold')),
        ('silver', _('Silver')),
        ('bronze', _('Bronze')),
        ('in-kind', _('In-Kind Contribution')),
        ('community', _('Community Sponsor')),
    ]

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='sponsors',
        verbose_name=_("Event")
    )

    # Can link to organization or be standalone
    organization = models.ForeignKey(
        'organization.Organization',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='sponsored_events',
        verbose_name=_("Organization")
    )
    sponsor_name = models.CharField(
        max_length=255, verbose_name=_("Sponsor name"))
    sponsor_logo = models.ImageField(
        upload_to='events/sponsors/',
        null=True,
        blank=True,
        verbose_name=_("Logo")
    )
    sponsor_website = models.URLField(blank=True, verbose_name=_("Website"))

    sponsor_type = models.CharField(
        max_length=20,
        choices=SPONSOR_TYPE,
        verbose_name=_("Sponsorship level")
    )

    # Financial or in-kind
    contribution_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_("Contribution amount")
    )
    contribution_description = models.TextField(
        blank=True,
        verbose_name=_("Contribution details"),
        help_text="Describe in-kind contributions or what the money supports"
    )

    # Display settings
    is_public = models.BooleanField(
        default=True,
        help_text="Show sponsor publicly on event page"
    )
    display_order = models.IntegerField(
        default=0, help_text="Sort order for display")

    # Metadata
    contributed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, help_text="Internal notes")

    objects = models.Manager()

    class Meta:
        """ Meta options for the EventSponsor model """
        verbose_name = _("Event Sponsor")
        verbose_name_plural = _("Event Sponsors")
        ordering = ['event', 'display_order', '-contribution_amount']

    def __str__(self):
        sponsor_display = self.get_sponsor_type_display()
        return (
            f"{self.sponsor_name} - {sponsor_display} ({self.event.title})"
        )


class EventExpense(models.Model):
    """
    Financial transparency - track all expenses with receipts.
    Critical for charity events and donor trust.
    """
    EXPENSE_CATEGORY = [
        ('materials', _('Materials & Supplies')),
        ('venue', _('Venue & Facilities')),
        ('food', _('Food & Catering')),
        ('transport', _('Transportation')),
        ('marketing', _('Marketing & Promotion')),
        ('equipment', _('Equipment Rental/Purchase')),
        ('staffing', _('Staffing & Labor')),
        ('permits', _('Permits & Licenses')),
        ('insurance', _('Insurance')),
        ('printing', _('Printing & Signage')),
        ('technology', _('Technology & Software')),
        ('other', _('Other')),
    ]

    STATUS_CHOICES = [
        ('pending', _('Pending Approval')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('paid', _('Paid')),
    ]

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='expenses',
        verbose_name=_("Event")
    )
    category = models.CharField(
        max_length=50,
        choices=EXPENSE_CATEGORY,
        verbose_name=_("Category")
    )
    title = models.CharField(max_length=255, verbose_name=_("Expense title"))
    description = models.TextField(verbose_name=_("Description"))

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_("Amount")
    )
    currency = models.CharField(max_length=3, default='USD')

    # Documentation
    receipt = models.FileField(
        upload_to='events/receipts/',
        null=True,
        blank=True,
        verbose_name=_("Receipt/Invoice")
    )
    receipt_number = models.CharField(max_length=100, blank=True)
    vendor_name = models.CharField(
        max_length=255, blank=True, verbose_name=_("Vendor/Supplier"))

    # Dates
    expense_date = models.DateField(verbose_name=_("Date of expense"))
    payment_date = models.DateField(
        null=True, blank=True, verbose_name=_("Payment date"))

    # Approval workflow
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending')
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submitted_expenses'
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='approved_expenses'
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    notes = models.TextField(blank=True, verbose_name=_("Notes"))
    rejection_reason = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    class Meta:
        """ Meta options for the EventExpense model """
        verbose_name = _("Event Expense")
        verbose_name_plural = _("Event Expenses")
        ordering = ['event', '-expense_date']

    def __str__(self):
        return (
            f"{self.title} - {self.amount} "
            f"{self.currency} ({self.event.title})"
        )


class EventTicket(models.Model):
    """
    Ticketing system for paid events.
    Supports multiple ticket types and pricing tiers.
    """
    TICKET_STATUS = [
        ('active', _('Active')),
        ('sold-out', _('Sold Out')),
        ('expired', _('Expired')),
        ('inactive', _('Inactive')),
    ]

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='tickets',
        verbose_name=_("Event")
    )

    # Ticket details
    name = models.CharField(max_length=255, verbose_name=_("Ticket name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))

    # Pricing
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        verbose_name=_("Price")
    )
    currency = models.CharField(max_length=3, default='USD')

    # Availability
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Total number of tickets available"
    )
    quantity_sold = models.IntegerField(default=0)
    max_per_order = models.IntegerField(
        default=10,
        validators=[MinValueValidator(1)],
        help_text="Maximum tickets per order"
    )

    # Sale period
    sale_start = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Sale start date")
    )
    sale_end = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Sale end date")
    )

    # Status & metadata
    status = models.CharField(
        max_length=20,
        choices=TICKET_STATUS,
        default='active',
        verbose_name=_("Status")
    )
    display_order = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    class Meta:
        """ Meta options for the EventTicket model """
        verbose_name = _("Event Ticket")
        verbose_name_plural = _("Event Tickets")
        ordering = ['event', 'display_order', 'price']

    def __str__(self):
        return f"{self.name} - {self.price} {self.currency} ({self.event.title})"

    @property
    def is_available(self):
        """Check if ticket is currently available for purchase"""
        now = timezone.now()

        if self.status != 'active':
            return False
        if self.quantity_sold >= self.quantity:
            return False
        if self.sale_start and now < self.sale_start:
            return False
        if self.sale_end and now > self.sale_end:
            return False

        return True

    @property
    def remaining_quantity(self):
        """Get number of tickets still available"""
        return max(0, self.quantity - self.quantity_sold)
