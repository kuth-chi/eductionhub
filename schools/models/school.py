import decimal
import os
import re
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from schools.models.base import DefaultField


class SchoolType(DefaultField):
    """This class represents a school type"""

    type = models.CharField(max_length=128, unique=True, db_index=True, blank=False)
    description = models.TextField(blank=True, default=_("Description about the school type"))
    icon = models.CharField(max_length=128, blank=True, null=True, help_text=_("Icon class for the school type (e.g., 'university')"))
    # Explicit default manager for type checkers (Pylint E1101: no-member)
    objects = models.Manager()

    def __str__(self):
        return str(self.type)

    class Meta:
        ordering = ["type"]
        verbose_name = _("School Type")
        verbose_name_plural = _("School Types") 


def school_logo_upload_path(instance, filename):
    """Generate a file path for new school logo uploads."""
    ext = filename.split(".")[-1]
    name = re.sub(r"[^a-zA-Z0-9_-]", "", instance.name) or "unnamed-school"
    filename = f"{name}-{uuid.uuid4()}.{ext}"
    return os.path.join("uploads/schools/logos/", filename)


def school_cover_image_upload_path(instance, filename):
    """Generate a file path for new school logo uploads."""
    ext = filename.split(".")[-1]
    name = re.sub(r"[^a-zA-Z0-9_-]", "", instance.name) or "unnamed-school"
    filename = f"{name}-{uuid.uuid4()}.{ext}"
    return os.path.join("uploads/schools/cover/", filename)


class Address(models.Model):
    """Represents address model"""

    uuid = models.UUIDField(
        unique=True, default=uuid.uuid4, verbose_name=_("unique identifier")
    )
    name = models.CharField(max_length=128, blank=True, verbose_name=_("name"))
    street = models.CharField(max_length=255, blank=True, verbose_name=_("street"))
    city = models.CharField(max_length=128, blank=True, verbose_name=_("city"))
    state = models.CharField(max_length=128, blank=True, verbose_name=_("state"))
    zip_code = models.CharField(max_length=10, blank=True, verbose_name=_("zip code"))
    country = models.CharField(max_length=128, blank=True, verbose_name=_("country"))
    slug = models.SlugField(max_length=255, blank=True, unique=True)

    # References
    schools = models.ManyToManyField("schools.School", related_name="school_addresses")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        "user.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created_by",
        verbose_name="Created By",
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(
                self.street
                + " "
                + self.city
                + " "
                + self.state
                + " "
                + self.zip_code
                + " "
                + self.country
            )
        super().save(*args, **kwargs)
        return super().save(*args, **kwargs)

    def __str__(self):
        return (
            str(self.street)
            + ", "
            + str(self.city)
            + ", "
            + str(self.state)
            + ", "
            + str(self.zip_code)
            + ", "
            + str(self.country)
        )

    class Meta:
        verbose_name = _("address")
        verbose_name_plural = _("addresses")
        ordering = ["name"]
        unique_together = ["street", "city", "state", "zip_code", "country"]


class School(models.Model):
    """Represents for School models"""

    logo = models.ImageField(upload_to=school_logo_upload_path, null=True, blank=True, verbose_name=_("logo"))
    cover_image = models.ImageField(upload_to=school_cover_image_upload_path, null=True, blank=True, verbose_name=_("photo"))
    name = models.CharField(max_length=75, blank=True, verbose_name=_("name"))
    local_name = models.CharField(max_length=128, blank=True, verbose_name=_("local name"))
    short_name = models.CharField(max_length=25, blank=True, verbose_name=_("short name"))
    code = models.CharField(max_length=15, blank=True, verbose_name=_("code"))
    description = models.TextField(blank=True, default=_("The school description"))
    established = models.DateField(null=True, blank=True, verbose_name=_("established"))
    founder = models.CharField(max_length=125, blank=True, verbose_name=_("founder"))
    president = models.CharField(max_length=125, blank=True, verbose_name=_("president"))
    endowment = models.DecimalField(max_digits=18, decimal_places=2, blank=True, default=decimal.Decimal("0.00"),
        verbose_name=_("endowment"),
    )
    # Address fields
    street_address = models.CharField(max_length=255, blank=True, verbose_name=_("street address"))
    address_line_2 = models.CharField(max_length=255, blank=True, verbose_name=_("address line 2"))
    box_number = models.CharField(max_length=50, blank=True, verbose_name=_("box number"))
    postal_code = models.CharField(max_length=20, blank=True, verbose_name=_("postal code"))


    # Geo relationships
    country = models.ForeignKey(
        "geo.Country",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="schools",
        verbose_name=_("country"),
    )
    state = models.ForeignKey(
        "geo.State",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="schools",
        verbose_name=_("state"),
    )
    city = models.ForeignKey(
        "geo.City",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="schools",
        verbose_name=_("city"),
    )
    village = models.ForeignKey(
        "geo.Village",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="schools",
        verbose_name=_("village"),
    )

    # Legacy location field (for backward compatibility)
    location = models.CharField(max_length=255, blank=True, verbose_name=_("location"))

    motto = models.CharField(max_length=250, blank=True, verbose_name=_("motto"), default=_("N/A"))
    tuition = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        blank=True,
        default=decimal.Decimal("0.00"),
        verbose_name=(_("tuition")),
    )

    # References
    type = models.ManyToManyField("schools.SchoolType", verbose_name=_("type"))
    platforms = models.ManyToManyField(
        "schools.Platform",
        related_name="school_platforms",
        through="PlatformProfile",
        verbose_name=_("platforms"),
    )
    educational_levels = models.ManyToManyField(
        "schools.EducationalLevel",
        related_name="school_educational_levels",
        blank=True,
        verbose_name=_("school level"),
    )
    degree_levels = models.ManyToManyField(
        "schools.EducationDegree",
        related_name="school_education_degrees",
        blank=True,
        verbose_name=_("school eduction degree"),
    )
    organization = models.ForeignKey(
        "organization.Organization", on_delete=models.CASCADE, blank=True, null=True
    )


    slug = models.SlugField(max_length=75, blank=True, verbose_name=_("slug"))
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, verbose_name=_("unique identifier"))
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
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
            self.slug = slugify(self.name) + "-" + (str(uuid.uuid4())[:6])
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.name) or _("Unnamed School")

    class Meta:
        """Meta class used to handle UI and configuration"""

        ordering = ["name"]
        verbose_name = _("school")
        verbose_name_plural = _("schools")


class SchoolBranchContactInfo(models.Model):
    name = models.CharField(max_length=128, unique=True)
    contact_value = models.CharField(max_length=15, unique=True)
    slug = models.SlugField(max_length=255, blank=True, unique=True)
    contact_type = models.CharField(
        max_length=50,
        choices=[
            ("phone", _("Phone")),
            ("email", _("Email")),
            ("website", _("Website")),
            ("social_media", _("Social Media")),
        ],
        default="phone",
        verbose_name=_("contact type"),
    )
    # ForeignKey
    branch = models.ForeignKey(
        "schools.SchoolBranch",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="contact_info",
        verbose_name=_("branch"),
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey("user.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created_by",
        verbose_name="Created By",
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify((str(self.name or "")).lower() + "-" + (str(self.contact_value or "")))
        super().save(*args, **kwargs)
        return super().save(*args, **kwargs)

    def __str__(self):
        if not self.name:
            return _("Unnamed Contact Info")
        return self.name

    class Meta:
        verbose_name = _("School Branch Contact Info")
        verbose_name_plural = _("School Branch Contact Info")
        ordering = ["name"]


class SchoolBranch(models.Model):
    """Enhanced school branch model with headquarters identification"""

    uuid = models.UUIDField(unique=True, default=uuid.uuid4, verbose_name=_("unique ID"))
    name = models.CharField(max_length=255, verbose_name=_("Branch Name"))
    short_name = models.CharField(max_length=100, blank=True, verbose_name=_("Short Name"))

    # Headquarters identification
    is_headquarters = models.BooleanField(default=False, verbose_name=_("Is Headquarters"))
    headquarters_branch = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sub_branches",
        verbose_name=_("Headquarters Branch"),
    )

    # Location and contact
    address = models.TextField(verbose_name=_("Address"))
    village = models.ForeignKey("geo.Village", on_delete=models.CASCADE, blank=True, null=True, related_name="branches")
    city = models.ForeignKey("geo.City", on_delete=models.CASCADE, blank=True, null=True, related_name="branches")
    state = models.ForeignKey("geo.State", on_delete=models.CASCADE, blank=True, null=True, related_name="branches")
    country = models.ForeignKey("geo.Country", on_delete=models.CASCADE, blank=True, null=True, related_name="branches")
    zip_code = models.CharField(max_length=20, blank=True, verbose_name=_("ZIP Code"))
    location = models.CharField(
        max_length=255, blank=True, verbose_name=_("Location"),
        help_text=_("Geographical location or coordinates")
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name=_("Phone"))
    email = models.EmailField(blank=True, verbose_name=_("Email"))
    website = models.URLField(blank=True, verbose_name=_("Website"))

    # Academic offerings
    degrees_offered = models.ManyToManyField("schools.EducationDegree", related_name="school_branches", blank=True)
    majors_offered = models.ManyToManyField("schools.Major", related_name="school_branches", blank=True)
    school = models.ForeignKey("schools.School", on_delete=models.CASCADE, blank=True, null=True, related_name="school_branches", verbose_name=_("School"))
    # Branch details
    established_year = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Established Year"))
    student_capacity = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Student Capacity"))
    description = models.TextField(blank=True, verbose_name=_("Description"))

    # Metadata
    slug = models.SlugField(max_length=255, blank=True, unique=True, verbose_name=_("slug"))
    created_by = models.ForeignKey(
        "user.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_branches",
        verbose_name=_("Created By"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name) + "-" + str(uuid.uuid4())[:6]
        super().save(*args, **kwargs)

    def __str__(self):
        name = self.name if self.name else _("Unnamed Branch")
        return f"{str(name)} ({'HQ' if self.is_headquarters else 'Branch'})"

    class Meta:
        ordering = ["-is_headquarters", "name"]
        verbose_name = _("School Branch")
        verbose_name_plural = _("School Branches")

class SchoolCustomizeButton(models.Model):
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, related_name="custom_buttons"
    )
    order_number = models.PositiveIntegerField(
        default=0, help_text="Display order of the button."
    )
    name = models.CharField(
        max_length=100, default="Untitled", help_text="Text displayed on the button."
    )
    link = models.URLField(help_text="Target URL when button is clicked.")
    color = models.CharField(
        max_length=7,
        default="#1D4ED8",
        help_text="Hex color for the button background.",
    )
    text_color = models.CharField(
        max_length=7, default="#FFFFFF", help_text="Hex color for the button text."
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Optional icon class (e.g. 'fa fa-book') or emoji.",
    )
    is_visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    class Meta:
        ordering = ["order_number"]
        verbose_name = "Custom School Button"
        verbose_name_plural = "Custom School Buttons"

    def __str__(self):
        return f"{self.name} ({self.school.name})"

class FieldOfStudy(models.Model):
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=50, blank=True, null=True, unique=True)
    level = models.CharField(
        max_length=50,
        choices=[
            ("undergraduate", "Undergraduate"),
            ("graduate", "Graduate"),
            ("postgraduate", "Postgraduate"),
            ("phd", "PhD"),
        ],
        blank=True,
        null=True,
    )

    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    schools = models.ManyToManyField(
        "schools.School", related_name="fields_of_study", blank=True
    )
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    created_by = models.ForeignKey("user.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created_by",
        verbose_name="Created By",
    )

    def __str__(self):
        if not self.name:
            return _("Unnamed Field of Study")
        return self.name


class SchoolScholarship(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    school = models.ForeignKey("schools.School", on_delete=models.CASCADE)
    scholarship = models.ForeignKey("schools.Scholarship", on_delete=models.CASCADE)
    updated_date = models.DateTimeField(auto_now=True)
    created_date = models.DateTimeField(auto_now_add=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey("user.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created_by",
        verbose_name="Created By",
    )
    objects = models.Manager()

    def __str__(self):
        return f"{self.school.name} - {self.scholarship.name}"

    class Meta:
        verbose_name = _("Scholarship by school")
        verbose_name_plural = _("Scholarship by schools")


class OrganizationScholarship(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    organization = models.ForeignKey(
        "organization.Organization", on_delete=models.CASCADE
    )
    scholarship = models.ForeignKey("schools.Scholarship", on_delete=models.CASCADE)
    updated_date = models.DateTimeField(auto_now=True)
    created_date = models.DateTimeField(auto_now_add=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey("user.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created_by",
        verbose_name="Created By",
    )

    def __str__(self):
        return f"{self.organization.name} - {self.scholarship.name}"

    class Meta:
        verbose_name = _("Scholarship by organization")
        verbose_name_plural = _("Scholarship by organizations")
