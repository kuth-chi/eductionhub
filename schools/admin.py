from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from schools.models.OnlineProfile import Platform, PlatformProfile
from schools.models.levels import EducationalLevel
from schools.models.schoolsModel import FieldOfStudy, ScholarshipType, SchoolScholarship, SchoolType, School, SchoolCustomizeButton

# Register your models here.
@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'icon')
    search_fields = ('name',)

@admin.register(PlatformProfile)
class PlatformProfileAdmin(admin.ModelAdmin):
    list_display = ('school', 'platform', 'profile_url', 'created_date')
    search_fields = ('school__name', 'platform__name', 'username')
    list_filter = ('platform',) 
    
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'local_name', 'short_name', 'established', 'location', 'logo_preview', 'cover_preview')
    search_fields = ('name', 'local_name', 'short_name', 'description', 'location')
    list_filter = ('established', 'type')
    readonly_fields = ('logo_preview', 'cover_preview',)

    def logo_preview(self, obj):
        """ Show a preview of the logo image if it exists """
        if obj.logo:
            return format_html('<img src="{}" width="50" height="50" />', obj.logo.url)
        return "No logo"
    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" width="50" height="50" />', obj.cover_image.url)
        return "No cover"

    logo_preview.short_description = 'Logo Preview'
    cover_preview.short_description = "Cover Preview"

class SchoolCustomizeButtonInline(admin.TabularInline):
    model = SchoolCustomizeButton
    extra = 1  # Number of blank buttons shown by default
    fields = ('order_number', 'name', 'link', 'color', 'text_color', 'icon', 'is_visible')
    ordering = ('order_number',)
    show_change_link = True

class SchoolTypeAdmin(admin.ModelAdmin):
    list_display = ("type", "description", "icon")
    search_fields = ("type", "description")
    list_filter = ("created_date",)

@admin.register(SchoolCustomizeButton)
class SchoolCustomizeButtonAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'order_number', 'is_visible')
    list_filter = ('is_visible',)
    search_fields = ('name', 'school__name')
    ordering = ('school', 'order_number')
    
class EducationalLevelAdmin(admin.ModelAdmin):
    list_display = ('level_name', 'color', 'created_date', 'updated_date')
    search_fields = ('level_name', 'color')
    list_filter = ('created_date', 'updated_date')

@admin.register(SchoolScholarship)
class SchoolScholarshipAdmin(admin.ModelAdmin):
    list_display = ('school', 'scholarship', 'created_date', 'updated_date')
    search_fields = ('school__name', 'scholarship__name')
    list_filter = ('school', 'scholarship', 'created_date')
    readonly_fields = ('uuid', 'created_date', 'updated_date')

@admin.register(ScholarshipType)
class ScholarshipTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "is_need_based", "is_merit_based", "is_athletic", "created_at")
    list_filter = ("is_active", "is_need_based", "is_merit_based", "is_athletic")
    search_fields = ("name", "description")
    ordering = ("name",)

@admin.register(FieldOfStudy)
class FieldOfStudyAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'level', 'created_at')
    search_fields = ('name', 'code', 'description')
    list_filter = ('level', 'created_at')

admin.site.register(SchoolType, SchoolTypeAdmin)
admin.site.register(School, SchoolAdmin)
admin.site.register(EducationalLevel, EducationalLevelAdmin)
admin.site.site_header = _("Education Hub Admin System" ) 
admin.site.site_title = _("Education Administrator System")
admin.site.index_title = _("Welcome to Education Hub Admin System")
