# schools/models/scholarship.py
import os
import re
import uuid

from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext as _

from geo.models import Country


def scholarship_thumbnail_upload_path(instance, filename):
    """Generate a file path for new scholarship thumbnail uploads."""
    ext = filename.split(".")[-1]
    name = re.sub(r"[^a-zA-Z0-9_-]", "", instance.name) or "untitled"
    filename = f"{name}-{uuid.uuid4()}.{ext}"
    return os.path.join("uploads/scholarship/thumbnails/", filename)


class Scholarship(models.Model):
    """Represents a scholarship offered by institutions or organizations"""

    # Unique Identifier
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    slug = models.SlugField(
        max_length=255, unique=True, verbose_name="Scholarship Slug"
    )

    # Basic Information
    thumbnail = models.ImageField(
        upload_to=scholarship_thumbnail_upload_path,
        null=True,
        blank=True,
        verbose_name=_("thumbnail"),
    )
    name = models.CharField(
        max_length=255, unique=True, verbose_name="Scholarship Name"
    )
    local_name = models.CharField(
        max_length=255, blank=True, verbose_name="Scholarship Local Name"
    )

    description = models.TextField(
        blank=True, verbose_name="Scholarship Description")
    local_description = models.TextField(
        blank=True, verbose_name="Scholarship Local Description"
    )
    provider = models.CharField(
        max_length=255, blank=True, verbose_name="Scholarship Provider"
    )
    destination_countries = models.ManyToManyField(
        Country, related_name="destination_scholarships"
    )
    website = models.URLField(blank=True, verbose_name="Application Website")

    # Financial Details
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Scholarship Amount",
    )
    full_tuition_coverage = models.BooleanField(
        default=False, verbose_name="Full Tuition Coverage"
    )
    stipend = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Monthly Stipend",
    )

    # Eligibility Criteria
    eligibility_criteria = models.TextField(
        blank=True, verbose_name="Eligibility Criteria"
    )
    min_gpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Minimum GPA Requirement",
    )
    required_documents = models.TextField(
        blank=True, verbose_name="Required Documents")

    # Target Audience
    target_countries = models.ManyToManyField(
        "geo.Country", blank=True, verbose_name="Eligible Countries"
    )
    target_levels = models.ManyToManyField(
        "schools.EducationalLevel", blank=True, verbose_name="Eligible Education Levels"
    )
    target_fields = models.ManyToManyField(
        "schools.FieldOfStudy", blank=True, verbose_name="Eligible Fields of Study"
    )

    # Application Process
    application_deadline = models.DateField(
        null=True, blank=True, verbose_name="Application Deadline"
    )
    application_open_date = models.DateField(
        null=True, blank=True, verbose_name="Application Open Date"
    )
    application_status = models.CharField(
        max_length=50,
        choices=[("Open", "Open"), ("Closed", "Closed"),
                 ("Upcoming", "Upcoming")],
        default="Upcoming",
        verbose_name="Application Status",
    )

    # Additional Features
    renewable = models.BooleanField(
        default=False, verbose_name="Is Renewable?")
    duration = models.CharField(
        max_length=255, blank=True, verbose_name="Duration of Scholarship"
    )
    contact_email = models.EmailField(blank=True, verbose_name="Contact Email")
    notes = models.TextField(blank=True, verbose_name="Additional Notes")
    type = models.ForeignKey(
        "schools.ScholarshipType", on_delete=models.SET_NULL, null=True, blank=True
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    created_by = models.ForeignKey("user.User",
                                   on_delete=models.SET_NULL,
                                   null=True,
                                   blank=True,
                                   related_name="%(class)s_created_by",
                                   verbose_name="Created By",
                                   )
    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.slug:
            name = str(self.name).lower() if self.name else ""
            provider = str(self.provider).lower() if self.provider else ""
            self.slug = slugify(
                name
                + "-"
                + provider
                + "-"
                + str(uuid.uuid4())[:6]
            )
        super().save(*args, **kwargs)
        return super().save(*args, **kwargs)

    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ["name"]
        verbose_name = "Scholarship"
        verbose_name_plural = "Scholarships"


class ScholarshipType(models.Model):
    uuid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=100, unique=True,
                            verbose_name=_("Type Name"))
    description = models.TextField(
        blank=True, null=True, verbose_name=_("Description"))

    is_need_based = models.BooleanField(
        default=False, help_text="Does this require financial need?"
    )
    is_merit_based = models.BooleanField(
        default=False, help_text="Is this based on academic/skill merit?"
    )
    is_athletic = models.BooleanField(
        default=False, help_text="Is this for athletic performance?"
    )
    is_organization_specific = models.BooleanField(
        default=False, help_text="Linked to specific organization?"
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey("user.User",
                                   on_delete=models.SET_NULL,
                                   null=True,
                                   blank=True,
                                   related_name="%(class)s_created_by",
                                   verbose_name="Created By",
                                   )

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = _("Scholarship Type")
        verbose_name_plural = _("Scholarship Types")
        ordering = ["name"]
