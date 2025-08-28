from django.db import models
from schools.models.base import DefaultField
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import City, State, Country

class Country(DefaultField):
    """Country model for global location hierarchy"""

    name = models.CharField(max_length=255, unique=True)
    local_name = models.CharField(max_length=255, blank=True)
    code = models.CharField(
        max_length=3, unique=True, help_text="ISO 3166-1 alpha-3 country code"
    )
    phone_code = models.CharField(
        max_length=10, blank=True, help_text="International phone code"
    )
    flag_emoji = models.CharField(
        max_length=10, blank=True, help_text="Country flag emoji"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Country"
        verbose_name_plural = "Countries"
        ordering = ["name"]

    def __str__(self):
        if self.name:
            return self.name
        return "unknown"


class State(DefaultField):
    """State/Province model within a country"""

    name = models.CharField(max_length=255)
    local_name = models.CharField(max_length=255, blank=True)
    code = models.CharField(max_length=10, blank=True, help_text="State/province code")
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, related_name="states"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "State"
        verbose_name_plural = "States"
        ordering = ["country", "name"]
        unique_together = ["name", "country"]

    def __str__(self):
        return f"{self.name}, {self.country.name}"


class City(DefaultField):
    """City model within a state"""

    name = models.CharField(max_length=255)
    local_name = models.CharField(max_length=255, blank=True)
    code = models.CharField(max_length=10, blank=True, help_text="City code")
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name="cities")
    is_capital = models.BooleanField(
        default=False, help_text="Is this the capital city of the state?"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "City"
        verbose_name_plural = "Cities"
        ordering = ["state", "name"]
        unique_together = ["name", "state"]

    def __str__(self):
        return f"{self.name}, {self.state.name}, {self.state.country.name}"

    @property
    def country(self):
        """Get the country of this city"""
        return self.state.country


class Village(DefaultField):
    """Village/Suburb model within a city"""

    name = models.CharField(max_length=255)
    local_name = models.CharField(max_length=255, blank=True)
    code = models.CharField(max_length=10, blank=True, help_text="Village code")
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="villages")
    is_active = models.BooleanField(default=True)
    objects = models.Manager()

    class Meta:
        verbose_name = "Village"
        verbose_name_plural = "Villages"
        ordering = ["city", "name"]
        unique_together = ["name", "city"]

    def __str__(self):
        return f"{self.name}, {self.city.name}, {self.city.state.name}, {self.city.state.country.name}"

    @property
    def state(self):
        return getattr(self.city, "state")

    @property
    def country(self):
        return getattr(self.city, "country")

