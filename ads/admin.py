# admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import AdSpace, AdType, AdManager, AdPlacement, UserProfile, UserBehavior, AdImpression, AdClick

@admin.register(AdSpace)
class AdSpaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')

@admin.register(AdType)
class AdTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(AdManager)
class AdManagerAdmin(admin.ModelAdmin):
    list_display = ('campaign_title', 'ad_type', 'start_datetime', 'end_datetime', 'is_active', 'poster_preview')
    list_filter = ('ad_type', 'is_active')
    search_fields = ('campaign_title', 'tags')

    def poster_preview(self, obj):
        if obj.poster:
            return format_html('<img src="{}" style="height: 60px;" />', obj.poster.url)
        return "No Image"

    poster_preview.short_description = "Poster"

@admin.register(AdPlacement)
class AdPlacementAdmin(admin.ModelAdmin):
    list_display = ('ad', 'ad_space', 'position', 'is_primary')
    list_filter = ('ad_space',)
    ordering = ('ad_space', 'position')
    autocomplete_fields = ['ad', 'ad_space']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'last_active')
    search_fields = ('user_id',)

@admin.register(UserBehavior)
class UserBehaviorAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'session_id', 'page_slug', 'category', 'timestamp')
    search_fields = ('user_id', 'session_id', 'page_slug', 'category')

@admin.register(AdImpression)
class AdImpressionAdmin(admin.ModelAdmin):
    list_display = ('ad', 'user_id', 'session_id', 'timestamp', 'ip_address')
    search_fields = ('user_id', 'session_id')

@admin.register(AdClick)
class AdClickAdmin(admin.ModelAdmin):
    list_display = ('ad', 'user_id', 'timestamp')
    search_fields = ('user_id',)

