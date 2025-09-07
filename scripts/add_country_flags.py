#!/usr/bin/env python3
"""
Script to add flag emojis to countries in the database.
This script adds popular country flags to make the interface more visually appealing.
"""

from geo.models import Country
import os
import sys

import django

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()


# Country code to flag emoji mapping
COUNTRY_FLAGS = {
    # Major countries and their flag emojis
    'USA': '🇺🇸',
    'CAN': '🇨🇦',
    'GBR': '🇬🇧',
    'FRA': '🇫🇷',
    'DEU': '🇩🇪',
    'ITA': '🇮🇹',
    'ESP': '🇪🇸',
    'NLD': '🇳🇱',
    'BEL': '🇧🇪',
    'CHE': '🇨🇭',
    'AUT': '🇦🇹',
    'DNK': '🇩🇰',
    'SWE': '🇸🇪',
    'NOR': '🇳🇴',
    'FIN': '🇫🇮',
    'ISL': '🇮🇸',
    'IRL': '🇮🇪',
    'PRT': '🇵🇹',
    'GRC': '🇬🇷',
    'POL': '🇵🇱',
    'CZE': '🇨🇿',
    'SVK': '🇸🇰',
    'HUN': '🇭🇺',
    'ROU': '🇷🇴',
    'BGR': '🇧🇬',
    'HRV': '🇭🇷',
    'SVN': '🇸🇮',
    'EST': '🇪🇪',
    'LVA': '🇱🇻',
    'LTU': '🇱🇹',
    'RUS': '🇷🇺',
    'UKR': '🇺🇦',
    'BLR': '🇧🇾',
    'MDA': '🇲🇩',
    # Asian countries
    'CHN': '🇨🇳',
    'JPN': '🇯🇵',
    'KOR': '🇰🇷',
    'PRK': '🇰🇵',
    'IND': '🇮🇳',
    'PAK': '🇵🇰',
    'BGD': '🇧🇩',
    'LKA': '🇱🇰',
    'NPL': '🇳🇵',
    'BTN': '🇧🇹',
    'MDV': '🇲🇻',
    'THA': '🇹🇭',
    'VNM': '🇻🇳',
    'LAO': '🇱🇦',
    'KHM': '🇰🇭',
    'MYS': '🇲🇾',
    'SGP': '🇸🇬',
    'IDN': '🇮🇩',
    'BRN': '🇧🇳',
    'PHL': '🇵🇭',
    'TWN': '🇹🇼',
    'HKG': '🇭🇰',
    'MAC': '🇲🇴',
    'MNG': '🇲🇳',
    'AFG': '🇦🇫',
    'IRN': '🇮🇷',
    'IRQ': '🇮🇶',
    'SYR': '🇸🇾',
    'LBN': '🇱🇧',
    'JOR': '🇯🇴',
    'ISR': '🇮🇱',
    'PSE': '🇵🇸',
    'SAU': '🇸🇦',
    'ARE': '🇦🇪',
    'QAT': '🇶🇦',
    'BHR': '🇧🇭',
    'KWT': '🇰🇼',
    'OMN': '🇴🇲',
    'YEM': '🇾🇪',
    'TUR': '🇹🇷',
    'GEO': '🇬🇪',
    'ARM': '🇦🇲',
    'AZE': '🇦🇿',
    'KAZ': '🇰🇿',
    'UZB': '🇺🇿',
    'TKM': '🇹🇲',
    'TJK': '🇹🇯',
    'KGZ': '🇰🇬',
    # African countries
    'EGY': '🇪🇬',
    'LBY': '🇱🇾',
    'TUN': '🇹🇳',
    'DZA': '🇩🇿',
    'MAR': '🇲🇦',
    'SDN': '🇸🇩',
    'SSD': '🇸🇸',
    'ETH': '🇪🇹',
    'ERI': '🇪🇷',
    'DJI': '🇩🇯',
    'SOM': '🇸🇴',
    'KEN': '🇰🇪',
    'UGA': '🇺🇬',
    'TZA': '🇹🇿',
    'RWA': '🇷🇼',
    'BDI': '🇧🇮',
    'ZAF': '🇿🇦',
    'NAM': '🇳🇦',
    'BWA': '🇧🇼',
    'ZWE': '🇿🇼',
    'ZMB': '🇿🇲',
    'MWI': '🇲🇼',
    'MOZ': '🇲🇿',
    'MDG': '🇲🇬',
    'MUS': '🇲🇺',
    'SYC': '🇸🇨',
    'COM': '🇰🇲',
    'AGO': '🇦🇴',
    'COD': '🇨🇩',
    'COG': '🇨🇬',
    'CAF': '🇨🇫',
    'TCD': '🇹🇩',
    'CMR': '🇨🇲',
    'NGA': '🇳🇬',
    'NER': '🇳🇪',
    'BFA': '🇧🇫',
    'MLI': '🇲🇱',
    'SEN': '🇸🇳',
    'GMB': '🇬🇲',
    'GNB': '🇬🇼',
    'GIN': '🇬🇳',
    'SLE': '🇸🇱',
    'LBR': '🇱🇷',
    'CIV': '🇨🇮',
    'GHA': '🇬🇭',
    'TGO': '🇹🇬',
    'BEN': '🇧🇯',
    'GAB': '🇬🇦',
    'GNQ': '🇬🇶',
    'STP': '🇸🇹',
    # Americas
    'MEX': '🇲🇽',
    'GTM': '🇬🇹',
    'BLZ': '🇧🇿',
    'SLV': '🇸🇻',
    'HND': '🇭🇳',
    'NIC': '🇳🇮',
    'CRI': '🇨🇷',
    'PAN': '🇵🇦',
    'CUB': '🇨🇺',
    'HTI': '🇭🇹',
    'DOM': '🇩🇴',
    'JAM': '🇯🇲',
    'PRI': '🇵🇷',
    'TTO': '🇹🇹',
    'GUY': '🇬🇾',
    'SUR': '🇸🇷',
    'GUF': '🇬🇫',
    'BRA': '🇧🇷',
    'VEN': '🇻🇪',
    'COL': '🇨🇴',
    'ECU': '🇪🇨',
    'PER': '🇵🇪',
    'BOL': '🇧🇴',
    'PRY': '🇵🇾',
    'URY': '🇺🇾',
    'ARG': '🇦🇷',
    'CHL': '🇨🇱',
    # Oceania
    'AUS': '🇦🇺',
    'NZL': '🇳🇿',
    'PNG': '🇵🇬',
    'FJI': '🇫🇯',
    'NCL': '🇳🇨',
    'SLB': '🇸🇧',
    'VUT': '🇻🇺',
    'TON': '🇹🇴',
    'WSM': '🇼🇸',
    'KIR': '🇰🇮',
    'TUV': '🇹🇻',
    'NRU': '🇳🇷',
    'PLW': '🇵🇼',
    'FSM': '🇫🇲',
    'MHL': '🇲🇭',
    'GUM': '🇬🇺',
    'PYF': '🇵🇫',
    'COK': '🇨🇰',
}


def add_flags_to_countries():
    """Add flag emojis to countries based on their ISO codes."""
    updated_count = 0
    total_countries = Country.objects.count()

    print(f"Starting to update flags for {total_countries} countries...")

    for country in Country.objects.all():
        if country.code in COUNTRY_FLAGS:
            old_flag = country.flag_emoji
            country.flag_emoji = COUNTRY_FLAGS[country.code]
            country.save()
            updated_count += 1
            print(
                f"✅ Updated {country.name} ({country.code}): {old_flag or 'None'} → {country.flag_emoji}")
        else:
            print(f"⚠️  No flag found for {country.name} ({country.code})")

    print(
        f"\n🎉 Completed! Updated {updated_count} out of {total_countries} countries with flag emojis.")


def main():
    """Main function to run the script."""
    try:
        add_flags_to_countries()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
