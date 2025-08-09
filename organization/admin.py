from django.contrib import admin

from organization.models.base import Industry, Organization
from organization.models.employee import Employee
from rbac.models.role_assignment import RoleAssignment

# Register your models here.
class OrganziationAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ['name']

class IndustryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')

class RoleAssignmentInline(admin.TabularInline):
    model = RoleAssignment
    extra = 0
    fields = ('role', 'key', 'value', 'is_active', 'is_deleted')
    readonly_fields = ('created_at', 'updated_at')
    show_change_link = True

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization', 'department', 'position', 'is_active')
    search_fields = ('user__username', 'organization__name', 'department')
    list_filter = ('is_active', 'is_deleted', 'department')
    inlines = [RoleAssignmentInline]


admin.site.register(Organization, OrganziationAdmin)
admin.site.register(Industry,IndustryAdmin)