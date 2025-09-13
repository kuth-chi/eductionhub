#!/usr/bin/env python
"""
Debug script to check ads data in the database
Run this script to see what ad spaces, campaigns, and placements exist
"""

from ads.models import AdManager, AdPlacement, AdSpace, AdType
import os
import sys

import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')
django.setup()


def debug_ads_data():
    print("=== ADS DEBUG INFORMATION ===\n")

    # Check Ad Spaces
    print("1. AD SPACES:")
    ad_spaces = AdSpace.objects.all()
    if ad_spaces:
        for space in ad_spaces:
            print(
                f"   - ID: {space.id}, Name: {space.name}, Slug: {space.slug}")
    else:
        print("   No ad spaces found!")
    print()

    # Check Ad Types
    print("2. AD TYPES:")
    ad_types = AdType.objects.all()
    if ad_types:
        for ad_type in ad_types:
            print(f"   - ID: {ad_type.id}, Name: {ad_type.name}")
    else:
        print("   No ad types found!")
    print()

    # Check Ad Campaigns
    print("3. AD CAMPAIGNS:")
    campaigns = AdManager.objects.all()
    if campaigns:
        for campaign in campaigns:
            status = "ACTIVE" if campaign.is_active else "INACTIVE"
            currently_active = "CURRENTLY_ACTIVE" if campaign.is_currently_active(
            ) else "NOT_CURRENTLY_ACTIVE"
            print(f"   - UUID: {campaign.uuid}")
            print(f"     Title: {campaign.campaign_title}")
            print(f"     Status: {status}, {currently_active}")
            print(
                f"     Type: {campaign.ad_type.name if campaign.ad_type else 'None'}")
            print(
                f"     Start: {campaign.start_datetime}, End: {campaign.end_datetime}")
            print(f"     Poster: {campaign.poster}")
            print()
    else:
        print("   No campaigns found!")
    print()

    # Check Ad Placements
    print("4. AD PLACEMENTS:")
    placements = AdPlacement.objects.all()
    if placements:
        for placement in placements:
            status = "ACTIVE" if placement.is_active else "INACTIVE"
            print(f"   - ID: {placement.id}, Status: {status}")
            print(
                f"     Ad Space: {placement.ad_space.name} (slug: {placement.ad_space.slug})")
            print(f"     Campaign: {placement.ad.campaign_title}")
            print(f"     Position: {placement.position}")
            print()
    else:
        print("   No placements found!")
    print()

    # Check specific home carousel placements
    print("5. HOME CAROUSEL PLACEMENTS:")
    home_carousel_slugs = ["home-slider-player",
                           "homepage-carousel", "home_slider_player"]

    for slug in home_carousel_slugs:
        try:
            space = AdSpace.objects.get(slug=slug)
            placements = AdPlacement.objects.filter(
                ad_space=space, is_active=True)
            print(f"   Space '{slug}' ({space.name}):")

            if placements:
                for placement in placements:
                    campaign = placement.ad
                    print(f"     - Campaign: {campaign.campaign_title}")
                    print(f"       Active: {campaign.is_active}")
                    print(
                        f"       Currently Active: {campaign.is_currently_active()}")
                    print(f"       Poster: {campaign.poster}")
            else:
                print(f"     No active placements found!")
            print()

        except AdSpace.DoesNotExist:
            print(f"   Ad space with slug '{slug}' does not exist")

    print("=== END DEBUG ===")


if __name__ == "__main__":
    debug_ads_data()
