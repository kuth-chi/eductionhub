from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from .models import (
    Attachment,
    Education,
    Experience,
    Profile,
    Letter,
    Hobby,
    Language,
    ProfileContact,
    Reference,
    Skill,
)


User = get_user_model()


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Profile"


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

    # Define fieldsets to display fields in the admin interface
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email")}),
        (
            "Permissions",
            {"fields": ("is_active", "is_staff", "is_superuser", "user_permissions")},
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2"),
            },
        ),
    )


class LettersAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "created_date")
    search_fields = ("user__username", "title")


class ExperienceAdmin(admin.ModelAdmin):
    list_display = ("user", "organization", "title", "start_date", "end_date")


class ProfileAdmin(admin.ModelAdmin):
    def user(self, obj):
        return obj.user.username

    list_display = ("user", "photo")
    search_fields = ("user__username", "photo")


class AttachmentAdmin(admin.ModelAdmin):
    def user(self, obj):
        return obj.user.username

    list_display = ("user", "attachment_type", "attachment_file")
    search_fields = ("user__username", "attachment_type")
    list_filter = ("user", "attachment_type")


class HobbyAdmin(admin.ModelAdmin):
    def user_full_name(self, obj):
        if not obj.First_name and not obj.Last_name:
            return obj.user.username
        return f"{obj.user.first_name} {obj.user.last_name}"

    list_display = ("user_full_name", "name")
    search_fields = ("user__username", "name")


class EducationAdmin(admin.ModelAdmin):
    def user_full_name(self, obj):
        if not obj.First_name and not obj.Last_name:
            return obj.user.username
        return f"{obj.user.first_name} {obj.user.last_name}"

    list_display = ("user_full_name", "institution", "degree", "start_date", "end_date")
    search_fields = ("user__username", "institution", "degree")


try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass  # User model wasn't registered


class LanguageAdmin(admin.ModelAdmin):
    def user_full_name(self, obj):
        if not obj.First_name and not obj.Last_name:
            return obj.user.username
        return f"{obj.user.first_name} {obj.user.last_name}"

    list_display = ("user", "name", "level", "is_native")


class SkillAdmin(admin.ModelAdmin):
    def user_full_name(self, obj):
        if not obj.First_name and not obj.Last_name:
            return obj.user.username
        return f"{obj.user.first_name} {obj.user.last_name}"

    list_display = ("user", "name", "level")


class ReferenceAdmin(admin.ModelAdmin):
    def user_full_name(self, obj):
        if not obj.First_name and not obj.Last_name:
            return obj.user.username
        return f"{obj.user.first_name} {obj.user.last_name}"

    list_display = ("user_full_name", "name", "phone", "email", "position")


class AttachmentAdmin(admin.ModelAdmin):
    list_display = ("name", "content_type", "file")
    search_fields = ("name", "content_type")
    list_filter = ("name", "content_type")


@admin.register(ProfileContact)
class ProfileContactAdmin(admin.ModelAdmin):
    list_display = (
        "profile",
        "platform",
        "username",
        "profile_url",
        "is_active",
        "created_date",
    )
    list_filter = ("platform", "is_active", "created_date")
    search_fields = ("username", "profile__name", "platform__name")


# Register the custom User admin
admin.site.register(User, UserAdmin)
admin.site.register(Experience, ExperienceAdmin)
admin.site.register(Education, EducationAdmin)
admin.site.register(Letter, LettersAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Hobby, HobbyAdmin)
admin.site.register(Language, LanguageAdmin)
admin.site.register(Skill, SkillAdmin)
admin.site.register(Reference, ReferenceAdmin)
admin.site.register(Attachment, AttachmentAdmin)
