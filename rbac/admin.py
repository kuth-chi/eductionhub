from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.auth.models import Permission
from rbac.models.role import Role
from rbac.models.role_assignment import RoleAssignment
from rbac.models.role_permission import RolePermission


# --- Custom Filter for Active Status ---

class ActiveStatusFilter(SimpleListFilter):
    title = 'Active Status'
    parameter_name = 'is_active'

    def lookups(self, request, model_admin):
        return [
            ('1', 'Active'),
            ('0', 'Inactive'),
        ]

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(is_active=True)
        elif self.value() == '0':
            return queryset.filter(is_active=False)
        return queryset


# --- Inline for Role Permissions ---

class RolePermissionInline(admin.TabularInline):
    model = RolePermission
    extra = 1
    autocomplete_fields = ['permission']
    verbose_name = "Assigned Permission"
    verbose_name_plural = "Role Permissions"


# --- Role Admin ---

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'is_active', 'is_deleted', 'created_at')
    list_filter = ('organization', 'is_active', 'is_deleted')
    search_fields = ('name', 'organization__name')
    readonly_fields = ('uuid', 'created_at', 'updated_at')
    inlines = [RolePermissionInline]
    autocomplete_fields = ['organization']
    ordering = ('-created_at',)


# --- RoleAssignment Admin ---

@admin.register(RoleAssignment)
class RoleAssignmentAdmin(admin.ModelAdmin):
    list_display = ('employee_display', 'role', 'key', 'value', 'is_active', 'created_at')
    list_filter = ('role', 'key', ActiveStatusFilter, 'created_at')
    search_fields = (
        'employee__user__username',
        'employee__organization__name',
        'role__name',
        'key',
        'value',
    )
    readonly_fields = ('uuid', 'created_at', 'updated_at')
    autocomplete_fields = ['employee', 'role']
    ordering = ('-created_at',)
    actions = ['make_active', 'make_inactive', 'soft_delete']

    def employee_display(self, obj):
        return f"{obj.employee.user.username} @ {obj.employee.organization.name}"
    employee_display.short_description = "Employee"

    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True, is_deleted=False)
        self.message_user(request, f"{updated} role assignments activated.")
    make_active.short_description = "Activate selected Role Assignments"

    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} role assignments deactivated.")
    make_inactive.short_description = "Deactivate selected Role Assignments"

    def soft_delete(self, request, queryset):
        updated = queryset.update(is_deleted=True)
        self.message_user(request, f"{updated} role assignments soft-deleted.")
    soft_delete.short_description = "Soft-delete selected Role Assignments"


# --- RolePermission Admin (Optional) ---

@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ('role', 'permission')
    search_fields = ('role__name', 'permission__codename')
    autocomplete_fields = ['role', 'permission']
    ordering = ('role__name',)


# --- Inline for ABAC Role Assignments (within Membership view) ---

class RoleAssignmentInline(admin.TabularInline):
    model = RoleAssignment
    extra = 0
    fields = ('role', 'key', 'value', 'is_active', 'is_deleted')
    readonly_fields = ('created_at', 'updated_at')
    show_change_link = True
    can_delete = True
    ordering = ('-created_at',)

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    search_fields = ('codename', 'name', 'content_type__app_label')
