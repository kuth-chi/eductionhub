"""
Fix flag_emoji for countries - convert country codes to actual emoji characters
"""
from geo.models import Country

def convert_code_to_flag(code):
    """Convert 2-letter country code to flag emoji"""
    if not code or len(code) < 2:
        return ""
    
    # Take first 2 characters and convert to uppercase
    code_2char = code[:2].upper()
    
    # Convert to regional indicator symbols (flag emoji)
    # Regional Indicator Symbol Letter A starts at 0x1F1E6
    flag_emoji = ''.join(
        chr(0x1F1E6 + ord(char) - ord('A')) 
        for char in code_2char 
        if char.isalpha()
    )
    
    return flag_emoji

# Fix Country ID 1 (Cambodia)
try:
    country = Country.objects.get(id=1)
    print(f"Current state:")
    print(f"  Name: {country.name}")
    print(f"  Code: {country.code}")
    print(f"  Flag Emoji (before): {repr(country.flag_emoji)}")
    
    # Convert code to flag emoji
    new_flag = convert_code_to_flag(country.code)
    
    if new_flag:
        country.flag_emoji = new_flag
        country.save()
        print(f"\n✅ Updated successfully!")
        print(f"  Flag Emoji (after): {repr(new_flag)}")
        print(f"  Display: {new_flag}")
    else:
        print(f"\n❌ Could not generate flag emoji from code: {country.code}")
        
except Country.DoesNotExist:
    print("❌ Country with ID 1 not found")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
