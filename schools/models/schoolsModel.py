import os
import re
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from schools.models.base import DefaultField
from organization.models import Organization
class SchoolType(DefaultField):
    """ This class represents a school type """
    type = models.CharField(max_length=128, unique=True,
                            db_index=True, blank=False)
    description = models.TextField(
        blank=True, default=_('Description about the school type'))
    icon = models.CharField(max_length=128, blank=True,)

    def __str__(self):
        return str(self.type)

    class Meta:
        ordering = ["type"]
        verbose_name = _('School Type')

def scholarship_thumbnail_upload_path(instance, filename):
    """ Generate a file path for new scholarship thumbnail uploads. """
    ext = filename.split('.')[-1]
    name = re.sub(r'[^a-zA-Z0-9_-]', '', instance.name) or "untitled"
    filename = f"{name}-{uuid.uuid4()}.{ext}"
    return os.path.join('uploads/scholarship/thumbnails/', filename)

def school_logo_upload_path(instance, filename):
    """ Generate a file path for new school logo uploads. """
    ext = filename.split('.')[-1]
    name = re.sub(r'[^a-zA-Z0-9_-]', '', instance.name) or "unnamed-school"
    filename = f"{name}-{uuid.uuid4()}.{ext}"
    return os.path.join('uploads/schools/logos/', filename)

def school_cover_image_upload_path(instance, filename):
    """ Generate a file path for new school logo uploads. """
    ext = filename.split('.')[-1]
    name = re.sub(r'[^a-zA-Z0-9_-]', '', instance.name) or "unnamed-school"
    filename = f"{name}-{uuid.uuid4()}.{ext}"
    return os.path.join('uploads/schools/cover/', filename)


class Country(models.Model):
    name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(max_length=255, blank=True, unique=True)
    local_name = models.CharField(max_length=128, blank=True)
    code = models.CharField(max_length=10, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.country.lower() + "-" + self.code)
        super().save(*args, **kwargs)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('country')
        verbose_name_plural = _('countries')
        ordering = ['name']
        unique_together = ['name', 'code']




class Address(models.Model):
    """ Represents address model """
    name = models.CharField(max_length=128, blank=True, verbose_name=_('name'))
    street = models.CharField(max_length=255, blank=True, verbose_name=_('street'))
    city = models.CharField(max_length=128, blank=True, verbose_name=_('city'))
    state = models.CharField(max_length=128, blank=True, verbose_name=_('state'))
    zip_code = models.CharField(max_length=10, blank=True, verbose_name=_('zip code'))
    country = models.CharField(max_length=128, blank=True, verbose_name=_('country'))
    slug = models.SlugField(max_length=255, blank=True, unique=True)

    # References
    schools = models.ManyToManyField('School', related_name="school_addresses")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.street + " " + self.city + " " + self.state + " " + self.zip_code + " " + self.country)
        super().save(*args, **kwargs)
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return str(self.street) + ", " + str(self.city) + ", " + str(self.state) + ", " + str(self.zip_code) + ", " + str(self.country)
    
    class Meta:
        verbose_name = _('address')
        verbose_name_plural = _('addresses')
        ordering = ['name']
        unique_together = ['street', 'city','state', 'zip_code', 'country']


class School(models.Model):
    """ Represents for School models """
    logo = models.ImageField(upload_to=school_logo_upload_path, null=True, blank=True, verbose_name=_('logo'))
    cover_image = models.ImageField(upload_to=school_cover_image_upload_path, null=True, blank=True, verbose_name=_('photo'))
    name = models.CharField(max_length=75, blank=True, verbose_name=_('name'))
    local_name = models.CharField(max_length=128, blank=True, verbose_name=_('local name'))
    short_name = models.CharField(max_length=25, blank=True, verbose_name=_('short name'))
    code = models.CharField(max_length=15, blank=True, verbose_name=_('code'))
    description = models.TextField(blank=True, default=_("The school description"))
    established = models.DateField(null=True, blank=True, verbose_name=_('established'))
    founder = models.CharField(max_length=125, blank=True, verbose_name=_('founder'))
    president = models.CharField(max_length=125, blank=True, verbose_name=_('president'))
    endowment = models.DecimalField(max_digits=18, decimal_places=2, blank=True, default=0.00, verbose_name=_('endowment'))
    location = models.CharField(max_length=255, blank=True, verbose_name=_('location'))
    motto = models.CharField(max_length=250, blank=True, verbose_name=_('motto'), default=_('N/A'))	
    tuition = models.DecimalField(max_digits=18, decimal_places=2, blank=True, default=0.00, verbose_name=(_("tuition")))
    
    # References
    type = models.ManyToManyField("SchoolType", verbose_name=_('type'))
    platforms = models.ManyToManyField("Platform", related_name="school_platforms", through="PlatformProfile", verbose_name=_('platforms'))
    educational_levels = models.ManyToManyField("EducationalLevel", related_name="school_educational_levels", blank=True, verbose_name=_("school level"))
    organization = models.ForeignKey("organization.Organization", on_delete=models.CASCADE, blank=True, null=True)
    # Tracking Fields
    slug = models.SlugField(max_length=75, blank=True, verbose_name=_('slug'))
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, verbose_name=_("unique identifier"))
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    self_data = models.CharField(max_length=128, blank=True, db_index=True, verbose_name=_("self data field"))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name) + "-" + (str(uuid.uuid4())[:6])
        super().save(*args, **kwargs)
    
    def __str__(self):
        return str(self.name) or _("Unnamed School")

    class Meta:
        ''' Meta class used to handle UI and configuration '''
        ordering = ['name']
        verbose_name = _("school")
        verbose_name_plural = _("schools")


class SchoolCustomizeButton(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="custom_buttons")
    order_number = models.PositiveIntegerField(default=0, help_text="Display order of the button.")
    name = models.CharField(max_length=100, default="Untitled", help_text="Text displayed on the button.")
    link = models.URLField(help_text="Target URL when button is clicked.")
    color = models.CharField(max_length=7, default="#1D4ED8", help_text="Hex color for the button background.")
    text_color = models.CharField(max_length=7, default="#FFFFFF", help_text="Hex color for the button text.")
    icon = models.CharField(max_length=50, blank=True, null=True, help_text="Optional icon class (e.g. 'fa fa-book') or emoji.")
    is_visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order_number"]
        verbose_name = "Custom School Button"
        verbose_name_plural = "Custom School Buttons"

    def __str__(self):
        return f"{self.name} ({self.school.name})"
    

class ScholarshipType(models.Model):
    uuid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Type Name"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))
    
    is_need_based = models.BooleanField(default=False, help_text="Does this require financial need?")
    is_merit_based = models.BooleanField(default=False, help_text="Is this based on academic/skill merit?")
    is_athletic = models.BooleanField(default=False, help_text="Is this for athletic performance?")
    is_organization_specific = models.BooleanField(default=False, help_text="Linked to specific organization?")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Scholarship Type")
        verbose_name_plural = _("Scholarship Types")
        ordering = ['name']


class Scholarship(models.Model):
    """ Represents a scholarship offered by institutions or organizations """
    
    # Unique Identifier
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    slug = models.SlugField(max_length=255, unique=True, verbose_name="Scholarship Slug")

    # Basic Information
    thumbnail = models.ImageField(upload_to=scholarship_thumbnail_upload_path, null=True, blank=True, verbose_name=_('thumbnail'))
    name = models.CharField(max_length=255, unique=True, verbose_name="Scholarship Name")
    local_name = models.CharField(max_length=255, blank=True, verbose_name="Scholarship Local Name")

    description = models.TextField(blank=True, verbose_name="Scholarship Description")
    local_description = models.TextField(blank=True, verbose_name="Scholarship Local Description")
    provider = models.CharField(max_length=255, blank=True, verbose_name="Scholarship Provider")
    destination_countries = models.ManyToManyField(Country, related_name="destination_scholarships")
    website = models.URLField(blank=True, verbose_name="Application Website")

    # Financial Details
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Scholarship Amount")
    full_tuition_coverage = models.BooleanField(default=False, verbose_name="Full Tuition Coverage")
    stipend = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Monthly Stipend")
    
    # Eligibility Criteria
    eligibility_criteria = models.TextField(blank=True, verbose_name="Eligibility Criteria")
    min_gpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="Minimum GPA Requirement")
    required_documents = models.TextField(blank=True, verbose_name="Required Documents")
    
    # Target Audience
    target_countries = models.ManyToManyField("Country", blank=True, verbose_name="Eligible Countries")
    target_levels = models.ManyToManyField("EducationalLevel", blank=True, verbose_name="Eligible Education Levels")
    target_fields = models.ManyToManyField("FieldOfStudy", blank=True, verbose_name="Eligible Fields of Study")

    # Application Process
    application_deadline = models.DateField(null=True, blank=True, verbose_name="Application Deadline")
    application_open_date = models.DateField(null=True, blank=True, verbose_name="Application Open Date")
    application_status = models.CharField(
        max_length=50, 
        choices=[("Open", "Open"), ("Closed", "Closed"), ("Upcoming", "Upcoming")], 
        default="Upcoming",
        verbose_name="Application Status"
    )

    # Additional Features
    renewable = models.BooleanField(default=False, verbose_name="Is Renewable?")
    duration = models.CharField(max_length=255, blank=True, verbose_name="Duration of Scholarship")
    contact_email = models.EmailField(blank=True, verbose_name="Contact Email")
    notes = models.TextField(blank=True, verbose_name="Additional Notes")
    type = models.ForeignKey("ScholarshipType", on_delete=models.SET_NULL, null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name.lower() + "-" + self.provider.lower() + "-" + str(uuid.uuid4())[:6])
        super().save(*args, **kwargs)
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "Scholarship"
        verbose_name_plural = "Scholarships"


class FieldOfStudy(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class SchoolScholarship(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    school = models.ForeignKey('School', on_delete=models.CASCADE)
    scholarship = models.ForeignKey('Scholarship', on_delete=models.CASCADE)
    updated_date = models.DateTimeField(auto_now=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.school.name} - {self.scholarship.name}"
    
    class Meta:
        verbose_name = _("Scholarship by school")
        verbose_name_plural = _("Scholarship by schools")


class OrganizationScholarship(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    scholarship = models.ForeignKey('Scholarship', on_delete=models.CASCADE)
    updated_date = models.DateTimeField(auto_now=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.school.name} - {self.scholarship.name}"
    
    class Meta:
        verbose_name = _("Scholarship by organization")
        verbose_name_plural = _("Scholarship by organization")