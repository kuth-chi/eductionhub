from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from schools.models.online_profile import Platform, PlatformProfile
from schools.models.scholarship import ScholarshipType
from schools.models.levels import (
    EducationDegree,
    EducationalLevel,
    College,
    Major,
    SchoolBranch,
    SchoolDegreeOffering,
    SchoolCollegeAssociation,
    SchoolMajorOffering,
)
from schools.models.school import (
    FieldOfStudy,
    SchoolBranchContactInfo,
    SchoolScholarship,
    SchoolType,
    School,
    SchoolCustomizeButton,
)


# Register your models here.
@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ("name", "url", "icon")
    search_fields = ("name",)


@admin.register(PlatformProfile)
class PlatformProfileAdmin(admin.ModelAdmin):
    list_display = ("school", "platform", "profile_url", "created_date")
    search_fields = ("school__name", "platform__name", "username")
    list_filter = ("platform",)


class SchoolAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "local_name",
        "short_name",
        "established",
        "location",
        "logo_preview",
        "cover_preview",
    )
    search_fields = ("name", "local_name", "short_name", "description", "location")
    list_filter = ("established", "type")
    readonly_fields = (
        "logo_preview",
        "cover_preview",
    )

    def logo_preview(self, obj):
        """Show a preview of the logo image if it exists"""
        if obj.logo:
            return format_html('<img src="{}" width="50" height="50" />', obj.logo.url)
        return "No logo"

    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" width="50" height="50" />', obj.cover_image.url
            )
        return "No cover"

    logo_preview.short_description = "Logo Preview"
    cover_preview.short_description = "Cover Preview"


class SchoolCustomizeButtonInline(admin.TabularInline):
    model = SchoolCustomizeButton
    extra = 1  # Number of blank buttons shown by default
    fields = (
        "order_number",
        "name",
        "link",
        "color",
        "text_color",
        "icon",
        "is_visible",
    )
    ordering = ("order_number",)
    show_change_link = True


class SchoolTypeAdmin(admin.ModelAdmin):
    list_display = ("type", "description", "icon")
    search_fields = ("type", "description")
    list_filter = ("created_date",)


@admin.register(SchoolCustomizeButton)
class SchoolCustomizeButtonAdmin(admin.ModelAdmin):
    list_display = ("name", "school", "order_number", "is_visible")
    list_filter = ("is_visible",)
    search_fields = ("name", "school__name")
    ordering = ("school", "order_number")


class EducationalLevelAdmin(admin.ModelAdmin):
    list_display = (
        "level_name",
        "order",
        "color",
        "parent_level",
        "created_date",
        "is_active",
    )
    search_fields = ("level_name", "color")
    list_filter = ("created_date", "is_active", "parent_level")
    ordering = ("order", "level_name")


@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "short_name",
        "email",
        "phone",
        "established_year",
        "is_active",
    )
    search_fields = ("name", "short_name", "email", "focus_areas")
    list_filter = ("established_year", "is_active", "created_at")
    readonly_fields = ("uuid", "created_at", "updated_at")
    fieldsets = (
        (
            "Basic Information",
            {"fields": ("name", "short_name", "description", "slug")},
        ),
        ("Contact Information", {"fields": ("email", "phone", "website", "address")}),
        ("Academic Focus", {"fields": ("focus_areas", "established_year")}),
        ("Status", {"fields": ("is_active", "is_deleted")}),
        (
            "Metadata",
            {"fields": ("uuid", "created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(Major)
class MajorAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "get_degrees",  # show degree names with a custom method
        "credit_hours",
        "duration_years",
        "is_active",
    )
    search_fields = ("name", "code", "description", "career_paths")
    list_filter = ("duration_years", "is_active", "created_at")
    readonly_fields = ("uuid", "created_at", "updated_at")
    filter_horizontal = ("colleges", "degrees") 

    fieldsets = (
        ("Basic Information", {"fields": ("name", "code", "description", "slug")}),
        ("Academic Details", {"fields": ("credit_hours", "duration_years", "degrees")}),
        ("Career & Industry", {"fields": ("career_paths", "industry_focus")}),
        ("Relationships", {"fields": ("colleges",)}),
        ("Status", {"fields": ("is_active", "is_deleted")}),
        ("Metadata", {"fields": ("uuid", "created_at", "updated_at"), "classes": ("collapse",)}),
    )

    @admin.display(description="Degrees")
    def get_degrees(self, obj):
        return ", ".join([deg.degree_name for deg in obj.degrees.all()])



@admin.register(SchoolBranch)
class SchoolBranchAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_headquarters",
        "city",
        "country",
        "established_year",
        "is_active",
    )
    search_fields = ("name", "short_name", "city__name", "country__name", "description")
    list_filter = ("is_headquarters", "established_year", "is_active", "created_at")
    readonly_fields = ("uuid", "created_at", "updated_at")

    filter_horizontal = ("degrees_offered", "majors_offered")  # model fields stay same

    fieldsets = (
        ("Basic Information", {"fields": ("name", "short_name", "description", "is_headquarters")}),
        ("Address", {"fields": ("address", "village", "city", "state", "country", "zip_code", "location")}),
        ("Contact Information", {"fields": ("phone", "email", "website")}),
        ("Academic Offerings", {"fields": ("degrees_offered", "majors_offered")}),
        ("Branch Details", {"fields": ("school", "established_year", "student_capacity")}),
        ("Status", {"fields": ("is_active", "is_deleted")}),
        ("Metadata", {"fields": ("slug", "uuid", "created_at", "updated_at"), "classes": ("collapse", "bg-primary",)}),
    )



@admin.register(SchoolDegreeOffering)
class SchoolDegreeOfferingAdmin(admin.ModelAdmin):
    list_display = (
        "school",
        "degree",
        "branch",
        "is_available",
        "enrollment_capacity",
        "current_enrollment",
    )
    search_fields = ("school__name", "degree__degree_name", "branch__name")
    list_filter = ("is_available", "degree", "branch", "created_at")
    readonly_fields = ("uuid", "created_at", "updated_at")
    fieldsets = (
        ("Relationship", {"fields": ("school", "degree", "branch")}),
        (
            "Offering Details",
            {"fields": ("is_available", "enrollment_capacity", "current_enrollment")},
        ),
        (
            "Academic Details",
            {"fields": ("duration_years", "credit_hours", "tuition_fee")},
        ),
        (
            "Application & Admission",
            {"fields": ("application_deadline", "admission_requirements")},
        ),
        ("Status", {"fields": ("is_active",)}),
        (
            "Metadata",
            {"fields": ("uuid", "created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(SchoolCollegeAssociation)
class SchoolCollegeAssociationAdmin(admin.ModelAdmin):
    list_display = (
        "school",
        "college",
        "branch",
        "is_active",
        "partnership_type",
        "established_date",
    )
    search_fields = ("school__name", "college__name", "partnership_type")
    list_filter = (
        "is_active",
        "partnership_type",
        "credit_transfer",
        "dual_degree",
        "created_at",
    )
    readonly_fields = ("uuid", "created_at", "updated_at")
    fieldsets = (
        ("Relationship", {"fields": ("school", "college", "branch")}),
        (
            "Association Details",
            {"fields": ("is_active", "partnership_type", "established_date")},
        ),
        (
            "Academic Collaboration",
            {"fields": ("joint_programs", "credit_transfer", "dual_degree")},
        ),
        (
            "Metadata",
            {"fields": ("uuid", "created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(SchoolMajorOffering)
class SchoolMajorOfferingAdmin(admin.ModelAdmin):
    list_display = (
        "school",
        "major",
        "degree",
        "branch",
        "is_available",
        "enrollment_capacity",
        "current_enrollment",
    )
    search_fields = (
        "school__name",
        "major__name",
        "degree__degree_name",
        "branch__name",
    )
    list_filter = ("is_available", "major", "degree", "branch", "created_at")
    readonly_fields = ("uuid", "created_at", "updated_at")
    fieldsets = (
        ("Relationship", {"fields": ("school", "major", "degree", "branch")}),
        (
            "Offering Details",
            {"fields": ("is_available", "enrollment_capacity", "current_enrollment")},
        ),
        (
            "Academic Details",
            {"fields": ("credit_hours", "duration_years", "tuition_fee")},
        ),
        ("Specializations", {"fields": ("specializations", "concentrations")}),
        ("Career & Industry", {"fields": ("career_outcomes", "industry_partners")}),
        (
            "Application & Admission",
            {
                "fields": (
                    "application_deadline",
                    "admission_requirements",
                    "gpa_requirement",
                )
            },
        ),
        ("Status", {"fields": ("is_active",)}),
        (
            "Metadata",
            {"fields": ("uuid", "created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(SchoolScholarship)
class SchoolScholarshipAdmin(admin.ModelAdmin):
    list_display = ("school", "scholarship", "created_date", "updated_date")
    search_fields = ("school__name", "scholarship__name")
    list_filter = ("school", "scholarship", "created_date")
    readonly_fields = ("uuid", "created_date", "updated_date")


@admin.register(ScholarshipType)
class ScholarshipTypeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_active",
        "is_need_based",
        "is_merit_based",
        "is_athletic",
        "created_at",
    )
    list_filter = ("is_active", "is_need_based", "is_merit_based", "is_athletic")
    search_fields = ("name", "description")
    ordering = ("name",)


@admin.register(FieldOfStudy)
class FieldOfStudyAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "level", "created_at")
    search_fields = ("name", "code", "description")
    list_filter = ("level", "created_at")


@admin.register(EducationDegree)
class EducationDegreeAdmin(admin.ModelAdmin):
    list_display = (
        "degree_name",
        "level",
        "duration_years",
        "credit_hours",
        "order",
        "is_active",
        "created_date",
        "updated_date",
    )
    search_fields = ("degree_name", "description")
    list_filter = ("level", "duration_years", "is_active", "created_date")
    ordering = ("order", "degree_name")
    readonly_fields = ("uuid",)

    fieldsets = (
        ("Basic Information", {"fields": ("degree_name", "description", "badge", "color", "slug")}),
        ("Academic Details", {"fields": ("level", "duration_years", "credit_hours")}),
        ("Hierarchy", {"fields": ("order", "parent_degree")}),
        ("Status", {"fields": ("is_active", "is_deleted")}),
        ("Metadata", {"fields": ("uuid",), "classes": ("collapse",)}),
    )


@admin.register(SchoolBranchContactInfo)
class SchoolBranchContactInfoAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "contact_value",
        "contact_type",
        "branch",
        "is_active",
        "is_deleted",
        "created_at",
        "updated_at",
    )
    list_filter = ("contact_type", "is_active", "is_deleted", "branch")
    search_fields = ("name", "contact_value", "slug")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
    prepopulated_fields = {"slug": ("name",)}

admin.site.register(SchoolType, SchoolTypeAdmin)
admin.site.register(School, SchoolAdmin)
admin.site.register(EducationalLevel, EducationalLevelAdmin)
# admin.site.register(EducationDegree, EducationDegreeAdmin)
admin.site.site_header = _("Education Hub Admin System")
admin.site.site_title = _("Education Administrator System")
admin.site.index_title = _("Welcome to Education Hub Admin System")
