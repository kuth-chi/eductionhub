from django.contrib import admin

from organization.models import Industry, Organization

# Register your models here.
class OrganziationAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')

class IndustryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')


admin.site.register(Organization, OrganziationAdmin)
admin.site.register(Industry,IndustryAdmin)