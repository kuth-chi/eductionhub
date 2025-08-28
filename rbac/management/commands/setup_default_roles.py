# rbac/management/commands/setup_default_roles.py
"""
Management command to set up default roles and permissions for the RBAC system.

Usage:
    python manage.py setup_default_roles
"""

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from rbac.models.role import Role
from schools.models.levels import SchoolBranch, College
from schools.models.school import School


class Command(BaseCommand):
    help = 'Set up default roles and permissions for the RBAC system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update existing roles',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Setting up default roles and permissions...')
        )

        force_update = options['force']

        # Define default roles with their permissions
        roles_permissions = {
            'SuperAdmin': {
                'description': 'Full system access with ability to delete schools and manage everything',
                'permissions': [
                    # School permissions
                    ('schools', 'school', 'add_school'),
                    ('schools', 'school', 'change_school'),
                    ('schools', 'school', 'delete_school'),
                    ('schools', 'school', 'view_school'),

                    # College permissions
                    ('schools', 'college', 'add_college'),
                    ('schools', 'college', 'change_college'),
                    ('schools', 'college', 'delete_college'),
                    ('schools', 'college', 'view_college'),

                    # Branch permissions
                    ('schools', 'branch', 'add_branch'),
                    ('schools', 'branch', 'change_branch'),
                    ('schools', 'branch', 'delete_branch'),
                    ('schools', 'branch', 'view_branch'),
                ]
            },
            'Administrator': {
                'description': 'School administrator with full management access except deleting schools',
                'permissions': [
                    # School permissions (no delete)
                    ('schools', 'school', 'add_school'),
                    ('schools', 'school', 'change_school'),
                    ('schools', 'school', 'view_school'),

                    # College permissions
                    ('schools', 'college', 'add_college'),
                    ('schools', 'college', 'change_college'),
                    ('schools', 'college', 'delete_college'),
                    ('schools', 'college', 'view_college'),

                    # Branch permissions
                    ('schools', 'branch', 'add_branch'),
                    ('schools', 'branch', 'change_branch'),
                    ('schools', 'branch', 'delete_branch'),
                    ('schools', 'branch', 'view_branch'),
                ]
            },
            'Manager': {
                'description': 'Department manager with college and branch management access',
                'permissions': [
                    # School permissions (view only)
                    ('schools', 'school', 'view_school'),

                    # College permissions
                    ('schools', 'college', 'add_college'),
                    ('schools', 'college', 'change_college'),
                    ('schools', 'college', 'delete_college'),
                    ('schools', 'college', 'view_college'),

                    # Branch permissions
                    ('schools', 'branch', 'add_branch'),
                    ('schools', 'branch', 'change_branch'),
                    ('schools', 'branch', 'delete_branch'),
                    ('schools', 'branch', 'view_branch'),
                ]
            },
            'Staff': {
                'description': 'Staff member with limited management access',
                'permissions': [
                    # School permissions (view only)
                    ('schools', 'school', 'view_school'),

                    # College permissions (no delete)
                    ('schools', 'college', 'add_college'),
                    ('schools', 'college', 'change_college'),
                    ('schools', 'college', 'view_college'),

                    # Branch permissions (no delete)
                    ('schools', 'branch', 'add_branch'),
                    ('schools', 'branch', 'change_branch'),
                    ('schools', 'branch', 'view_branch'),
                ]
            },
            'Viewer': {
                'description': 'Read-only access to all school information',
                'permissions': [
                    ('schools', 'school', 'view_school'),
                    ('schools', 'college', 'view_college'),
                    ('schools', 'branch', 'view_branch'),
                ]
            },
        }

        created_count = 0
        updated_count = 0

        for role_name, role_config in roles_permissions.items():
            # Create or get the role
            role, created = Role.objects.get_or_create(
                name=role_name,
                defaults={
                    'description': role_config['description'],
                    'is_active': True,
                }
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created role: {role_name}')
                )
            elif force_update:
                role.description = role_config['description']
                role.is_active = True
                role.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'⟳ Updated role: {role_name}')
                )

            # Create or get Django Group for compatibility
            group, group_created = Group.objects.get_or_create(name=role_name)
            if group_created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created group: {role_name}')
                )

            # Add permissions to the role and group
            for app_label, model_name, permission_codename in role_config['permissions']:
                try:
                    # Get the content type
                    content_type = ContentType.objects.get(
                        app_label=app_label,
                        model=model_name
                    )

                    # Get or create the permission
                    permission, perm_created = Permission.objects.get_or_create(
                        content_type=content_type,
                        codename=permission_codename,
                        defaults={
                            'name': f'Can {permission_codename.replace("_", " ")} {model_name}'
                        }
                    )

                    if perm_created:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'  ✓ Created permission: {permission_codename}')
                        )

                    # Add permission to role (if using custom RBAC)
                    if not role.permissions.filter(pk=permission.pk).exists():
                        role.permissions.add(permission)

                    # Add permission to group (for Django compatibility)
                    if not group.permissions.filter(pk=permission.pk).exists():
                        group.permissions.add(permission)

                except ContentType.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(
                            f'  ✗ Content type not found: {app_label}.{model_name}'
                        )
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'  ✗ Error setting up permission {permission_codename}: {e}'
                        )
                    )

        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Setup complete!'
                f'\n  - Created roles: {created_count}'
                f'\n  - Updated roles: {updated_count}'
                f'\n  - Total roles: {Role.objects.count()}'
            )
        )

        # Show current roles
        self.stdout.write('\nCurrent roles:')
        for role in Role.objects.filter(is_active=True).order_by('name'):
            perm_count = role.permissions.count()
            self.stdout.write(f'  • {role.name}: {perm_count} permissions')

        self.stdout.write(
            self.style.SUCCESS(
                '\nNext steps:'
                '\n1. Update your API views to use the new permission classes'
                '\n2. Assign roles to users: User.groups.add(group)'
                '\n3. Test the permission system'
            )
        )
