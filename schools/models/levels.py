import uuid
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class EducationalLevel(models.Model):
    """Represents different educational levels (Primary, Secondary, Higher Education, etc.)"""
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, verbose_name=_("unique ID"))
    level_name = models.CharField(max_length=75, unique=True, verbose_name=_("Level"))
    badge = models.CharField(max_length=125, blank=True, verbose_name=_("badge"))
    color = models.CharField(max_length=6, blank=True, verbose_name=_("color"))
    description = models.CharField(max_length=500, blank=True, default=_("No description"), verbose_name=_("description"))
    
    # Hierarchy and ordering
    order = models.PositiveIntegerField(default=0, help_text="Display order for sorting")
    parent_level = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='child_levels')
    
    # Metadata
    slug = models.SlugField(max_length=75, null=False, blank=False, verbose_name=_("slug"))
    created_date = models.DateField(auto_now_add=True, verbose_name=_("created at"))
    updated_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, verbose_name=_("status"))
    is_deleted = models.BooleanField(default=False, verbose_name=_("deleted"))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.level_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.level_name
    
    class Meta:
        ordering = ("order", "level_name", "-created_date", "updated_date")
        verbose_name = _("education level")
        verbose_name_plural = _("education levels")


class EducationDegree(models.Model):
    """Represents different degree types (Bachelor, Master, PhD, etc.)"""
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, verbose_name=_("unique ID"))
    degree_name = models.CharField(max_length=75, unique=True, verbose_name=_("Degree"))
    badge = models.CharField(max_length=125, blank=True, verbose_name=_("badge"))
    color = models.CharField(max_length=6, blank=True, verbose_name=_("color"))
    description = models.CharField(max_length=500, blank=True, default=_("No description"), verbose_name=_("description"))
    
    # Academic details
    duration_years = models.PositiveIntegerField(default=4, help_text="Typical duration in years")
    credit_hours = models.PositiveIntegerField(default=120, help_text="Required credit hours")
    level = models.ForeignKey(EducationalLevel, on_delete=models.CASCADE, related_name='degrees', null=True, blank=True)
    
    # Hierarchy and ordering
    order = models.PositiveIntegerField(default=0, help_text="Display order for sorting")
    parent_degree = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='child_degrees')
    
    # Metadata
    slug = models.SlugField(max_length=75, null=False, blank=False, verbose_name=_("slug"))
    created_date = models.DateField(auto_now_add=True, verbose_name=_("created at"))
    updated_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, verbose_name=_("status"))
    is_deleted = models.BooleanField(default=False, verbose_name=_("deleted"))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.degree_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.degree_name

    class Meta:
        ordering = ("degree_name", "-created_date", "updated_date")
        verbose_name = _("education degree")
        verbose_name_plural = _("education degrees")


class College(models.Model):
    """Represents colleges within educational institutions"""
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, verbose_name=_("unique ID"))
    name = models.CharField(max_length=255, verbose_name=_("College Name"))
    short_name = models.CharField(max_length=50, blank=True, verbose_name=_("Short Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    
    # Contact and location
    email = models.EmailField(blank=True, verbose_name=_("Email"))
    phone = models.CharField(max_length=20, blank=True, verbose_name=_("Phone"))
    website = models.URLField(blank=True, verbose_name=_("Website"))
    address = models.TextField(blank=True, verbose_name=_("Address"))
    
    # Academic focus
    focus_areas = models.TextField(blank=True, verbose_name=_("Focus Areas"))
    established_year = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Established Year"))
    
    # Metadata
    slug = models.SlugField(max_length=255, blank=True, unique=True, verbose_name=_("slug"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name) + "-" + str(uuid.uuid4())[:6]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = _("College")
        verbose_name_plural = _("Colleges")


class Major(models.Model):
    """Represents academic majors/programs of study"""
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, verbose_name=_("unique ID"))
    name = models.CharField(max_length=255, verbose_name=_("Major Name"))
    code = models.CharField(max_length=20, unique=True, verbose_name=_("Major Code"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    
    # Academic details
    credit_hours = models.PositiveIntegerField(default=120, verbose_name=_("Required Credit Hours"))
    duration_years = models.PositiveIntegerField(default=4, verbose_name=_("Duration (Years)"))
    
    # Relationships
    degree = models.ForeignKey(EducationDegree, on_delete=models.CASCADE, related_name='majors', null=True, blank=True)
    colleges = models.ManyToManyField(College, related_name='majors', blank=True)
    
    # Career and industry focus
    career_paths = models.TextField(blank=True, verbose_name=_("Career Paths"))
    industry_focus = models.CharField(max_length=255, blank=True, verbose_name=_("Industry Focus"))
    
    # Metadata
    slug = models.SlugField(max_length=255, blank=True, unique=True, verbose_name=_("slug"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name) + "-" + str(uuid.uuid4())[:6]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        ordering = ["name"]
        verbose_name = _("Major")
        verbose_name_plural = _("Majors")


class SchoolBranch(models.Model):
    """Enhanced school branch model with headquarters identification"""
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, verbose_name=_("unique ID"))
    name = models.CharField(max_length=255, verbose_name=_("Branch Name"))
    short_name = models.CharField(max_length=100, blank=True, verbose_name=_("Short Name"))
    
    # Headquarters identification
    is_headquarters = models.BooleanField(default=False, verbose_name=_("Is Headquarters"))
    headquarters_branch = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, 
                                            related_name='sub_branches', verbose_name=_("Headquarters Branch"))
    
    # Location and contact
    address = models.TextField(verbose_name=_("Address"))
    city = models.CharField(max_length=100, verbose_name=_("City"))
    state = models.CharField(max_length=100, verbose_name=_("State/Province"))
    country = models.CharField(max_length=100, verbose_name=_("Country"))
    zip_code = models.CharField(max_length=20, blank=True, verbose_name=_("ZIP Code"))
    phone = models.CharField(max_length=20, blank=True, verbose_name=_("Phone"))
    email = models.EmailField(blank=True, verbose_name=_("Email"))
    website = models.URLField(blank=True, verbose_name=_("Website"))
    
    # Academic offerings
    degrees_offered = models.ManyToManyField(EducationDegree, related_name='branch_degrees', blank=True)
    colleges = models.ManyToManyField(College, related_name='branch_colleges', blank=True)
    majors_offered = models.ManyToManyField(Major, related_name='branch_majors', blank=True)
    
    # Branch details
    established_year = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Established Year"))
    student_capacity = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Student Capacity"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    
    # Metadata
    slug = models.SlugField(max_length=255, blank=True, unique=True, verbose_name=_("slug"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name) + "-" + str(uuid.uuid4())[:6]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({'HQ' if self.is_headquarters else 'Branch'})"

    class Meta:
        ordering = ["-is_headquarters", "name"]
        verbose_name = _("School Branch")
        verbose_name_plural = _("School Branches")


class SchoolDegreeOffering(models.Model):
    """Many-to-many relationship between schools and degrees with additional details"""
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, verbose_name=_("unique ID"))
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name='degree_offerings')
    degree = models.ForeignKey(EducationDegree, on_delete=models.CASCADE, related_name='school_offerings')
    branch = models.ForeignKey(SchoolBranch, on_delete=models.CASCADE, related_name='degree_offerings', null=True, blank=True)
    
    # Offering details
    is_available = models.BooleanField(default=True, verbose_name=_("Available for Enrollment"))
    enrollment_capacity = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Enrollment Capacity"))
    current_enrollment = models.PositiveIntegerField(default=0, verbose_name=_("Current Enrollment"))
    
    # Academic details
    duration_years = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Duration (Years)"))
    credit_hours = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Credit Hours"))
    tuition_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("Tuition Fee"))
    
    # Application and admission
    application_deadline = models.DateField(null=True, blank=True, verbose_name=_("Application Deadline"))
    admission_requirements = models.TextField(blank=True, verbose_name=_("Admission Requirements"))
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.school.name} - {self.degree.degree_name}"

    class Meta:
        unique_together = ['school', 'degree', 'branch']
        ordering = ['school', 'degree']
        verbose_name = _("School Degree Offering")
        verbose_name_plural = _("School Degree Offerings")


class SchoolCollegeAssociation(models.Model):
    """Many-to-many relationship between schools and colleges with additional details"""
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, verbose_name=_("unique ID"))
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name='college_associations')
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='school_associations')
    branch = models.ForeignKey(SchoolBranch, on_delete=models.CASCADE, related_name='college_associations', null=True, blank=True)
    
    # Association details
    is_active = models.BooleanField(default=True, verbose_name=_("Active Association"))
    partnership_type = models.CharField(max_length=100, blank=True, verbose_name=_("Partnership Type"))
    established_date = models.DateField(null=True, blank=True, verbose_name=_("Partnership Established"))
    
    # Academic collaboration
    joint_programs = models.TextField(blank=True, verbose_name=_("Joint Programs"))
    credit_transfer = models.BooleanField(default=False, verbose_name=_("Credit Transfer Available"))
    dual_degree = models.BooleanField(default=False, verbose_name=_("Dual Degree Programs"))
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.school.name} - {self.college.name}"

    class Meta:
        unique_together = ['school', 'college', 'branch']
        ordering = ['school', 'college']
        verbose_name = _("School College Association")
        verbose_name_plural = _("School College Associations")


class SchoolMajorOffering(models.Model):
    """Many-to-many relationship between schools and majors with additional details"""
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, verbose_name=_("unique ID"))
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name='major_offerings')
    major = models.ForeignKey(Major, on_delete=models.CASCADE, related_name='school_offerings')
    branch = models.ForeignKey(SchoolBranch, on_delete=models.CASCADE, related_name='major_offerings', null=True, blank=True)
    degree = models.ForeignKey(EducationDegree, on_delete=models.CASCADE, related_name='major_offerings', null=True, blank=True)
    
    # Offering details
    is_available = models.BooleanField(default=True, verbose_name=_("Available for Enrollment"))
    enrollment_capacity = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Enrollment Capacity"))
    current_enrollment = models.PositiveIntegerField(default=0, verbose_name=_("Current Enrollment"))
    
    # Academic details
    credit_hours = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Credit Hours"))
    duration_years = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Duration (Years)"))
    tuition_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("Tuition Fee"))
    
    # Specializations and concentrations
    specializations = models.TextField(blank=True, verbose_name=_("Specializations"))
    concentrations = models.TextField(blank=True, verbose_name=_("Concentrations"))
    
    # Career and industry
    career_outcomes = models.TextField(blank=True, verbose_name=_("Career Outcomes"))
    industry_partners = models.TextField(blank=True, verbose_name=_("Industry Partners"))
    
    # Application and admission
    application_deadline = models.DateField(null=True, blank=True, verbose_name=_("Application Deadline"))
    admission_requirements = models.TextField(blank=True, verbose_name=_("Admission Requirements"))
    gpa_requirement = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True, 
                                           validators=[MinValueValidator(0.0), MaxValueValidator(4.0)], 
                                           verbose_name=_("Minimum GPA Requirement"))
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.school.name} - {self.major.name}"

    class Meta:
        unique_together = ['school', 'major', 'branch', 'degree']
        ordering = ['school', 'major']
        verbose_name = _("School Major Offering")
        verbose_name_plural = _("School Major Offerings")
