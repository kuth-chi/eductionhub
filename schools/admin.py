from django.contrib import admin

from schools.models.OnlineProfile import Platform, PlatformProfile

# Register your models here.
@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ('name', 'url')
    search_fields = ('name',)

@admin.register(PlatformProfile)
class PlatformProfileAdmin(admin.ModelAdmin):
    list_display = ('school', 'platform', 'profile_url', 'created_date')
    search_fields = ('school__name', 'platform__name', 'username')
    list_filter = ('platform',)