from django.contrib import admin
from .models import Country, State, City, Village


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "phone_code", "flag_emoji", "is_active")
    search_fields = ("name", "code")
    list_filter = ("is_active",)
    ordering = ("name",)


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "country", "is_active")
    search_fields = ("name", "code", "country__name")
    list_filter = ("country", "is_active")
    ordering = ("country__name", "name")


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "state", "country", "is_capital", "is_active")
    search_fields = ("name", "code", "state__name", "state__country__name")
    list_filter = ("state__country", "state", "is_capital", "is_active")
    ordering = ("state__country__name", "state__name", "name")


@admin.register(Village)
class VillageAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "city",
        "state",
        "country",
        "is_active",
    )
    search_fields = (
        "name",
        "code",
        "city__name",
        "city__state__name",
        "city__state__country__name",
    )
    list_filter = ("city__state__country", "city__state", "city", "is_active")
    ordering = ("city__state__country__name", "city__state__name", "city__name", "name")
