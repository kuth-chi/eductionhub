# Country Flag Display Implementation Guide

This document explains how country flags are displayed throughout the EducationHub application.

## 🏗️ **Architecture Overview**

### Backend (Django)
- **Model**: `geo/models.py` - Country model has `flag_emoji` field
- **Serializers**: `api/serializers/schools/locations.py` - Includes flag_emoji in responses
- **API**: Flag data is available through all country-related endpoints

### Frontend (React/Next.js)
- **Components**: Country flags are displayed in multiple components
- **Data**: Flags come from the country API responses
- **Display**: Flags are shown with country names consistently

## 📍 **Where Flags Are Displayed**

### 1. **Village Management Interface**
**File**: `src/modules/geo/ui/components/village-management.tsx`

#### Country Filter Dropdown
```tsx
// Multi-select country filter with flags
<GeoMultiSelectCombobox
  label="Countries"
  options={countries?.map((c) => ({
    id: c.id,
    name: c.name,
    flag: c.flag_emoji,
  })) || []}
  // ... other props
/>
```

#### Villages Table
```tsx
// Country column shows flag + name
<TableCell>
  <div className="flex items-center gap-2">
    <span>{village.country.flag_emoji || ""}</span>
    <span>{village.country.name}</span>
  </div>
</TableCell>
```

#### Create/Edit Forms
```tsx
// Country dropdown in forms shows flags
<SelectItem key={country.id} value={country.id.toString()}>
  <div className="flex items-center gap-2">
    <span>{country.flag_emoji || "🌍"}</span>
    <span>{country.name}</span>
  </div>
</SelectItem>
```

### 2. **Multi-Select Component Enhancement**
**Component**: `GeoMultiSelectCombobox`

```tsx
// Enhanced to display flags in dropdown options
<span className="flex items-center gap-2 flex-1">
  {opt.flag && <span>{opt.flag}</span>}
  <span>{opt.name}</span>
</span>
```

## 🎨 **Visual Design Patterns**

### Flag Display Rules
1. **With Flag**: `🇺🇸 United States`
2. **Without Flag**: `🌍 Unknown Country` (fallback globe emoji)
3. **Spacing**: Always 2px gap between flag and text
4. **Alignment**: Flags are left-aligned with country names

### Component Structure
```tsx
<div className="flex items-center gap-2">
  <span>{country.flag_emoji || "🌍"}</span>
  <span>{country.name}</span>
</div>
```

## 📊 **Data Structure**

### Country Object
```typescript
interface Country {
  id: number;
  uuid: string;
  name: string;
  local_name?: string;
  code: string;           // ISO 3166-1 alpha-3 (e.g., "USA")
  phone_code?: string;
  flag_emoji?: string;    // Unicode flag emoji (e.g., "🇺🇸")
  is_active: boolean;
}
```

### API Response Example
```json
{
  "id": 1,
  "uuid": "550e8400-e29b-41d4-a716-446655440000",
  "name": "United States",
  "local_name": "United States of America",
  "code": "USA",
  "phone_code": "+1",
  "flag_emoji": "🇺🇸",
  "is_active": true
}
```

## 🛠️ **Adding Flags to Database**

### Method 1: Using the Script
```bash
# Navigate to project directory
cd "d:\Documents\Business\EZ Startup\Apps\EducationHub\Apps\v0.0.2"

# Activate virtual environment
.venv\Scripts\activate

# Run the flag addition script
python scripts/add_country_flags.py
```

### Method 2: Django Admin
1. Go to Django Admin: `http://127.0.0.1:8000/admin/`
2. Navigate to **Geo > Countries**
3. Edit each country and add flag emoji to **Flag emoji** field
4. Save changes

### Method 3: Django Shell
```python
# Start Django shell
python manage.py shell

# Import models
from geo.models import Country

# Update a specific country
usa = Country.objects.get(code='USA')
usa.flag_emoji = '🇺🇸'
usa.save()

# Bulk update multiple countries
countries_flags = {
    'USA': '🇺🇸',
    'CAN': '🇨🇦',
    'GBR': '🇬🇧',
    # ... more countries
}

for code, flag in countries_flags.items():
    try:
        country = Country.objects.get(code=code)
        country.flag_emoji = flag
        country.save()
        print(f"Updated {country.name}: {flag}")
    except Country.DoesNotExist:
        print(f"Country with code {code} not found")
```

## 🔧 **Customization Options**

### 1. **Flag Size**
```css
/* Adjust flag emoji size */
.flag-emoji {
  font-size: 1.2em; /* Make flags larger */
}
```

### 2. **Fallback Icons**
```tsx
// Different fallback options
{country.flag_emoji || "🌍"}  // Globe (current)
{country.flag_emoji || "🏳️"}   // White flag
{country.flag_emoji || "🚩"}   // Red flag
{country.flag_emoji || "📍"}   // Location pin
```

### 3. **Custom Flag Sources**
```tsx
// Use custom flag images instead of emojis
<img 
  src={`/flags/${country.code.toLowerCase()}.svg`}
  alt={`${country.name} flag`}
  className="w-5 h-3 object-cover"
/>
```

## 🧪 **Testing Flag Display**

### 1. **Check API Response**
```bash
# Test country API endpoint
curl http://127.0.0.1:8000/api/v1/countries/simple/

# Expected response includes flag_emoji field
[
  {
    "id": 1,
    "name": "United States",
    "code": "USA",
    "flag_emoji": "🇺🇸"
  }
]
```

### 2. **Frontend Testing**
1. **Filter Dropdown**: Check country filter shows flags
2. **Table Display**: Verify village table shows country flags
3. **Forms**: Confirm create/edit forms display flags in country dropdown
4. **Mobile View**: Test flag display on mobile filter drawer

### 3. **Browser Compatibility**
- ✅ **Chrome**: Full emoji support
- ✅ **Firefox**: Full emoji support  
- ✅ **Safari**: Full emoji support
- ⚠️ **Edge**: Some older versions may not display all flags
- ⚠️ **IE**: Limited emoji support (fallback recommended)

## 🐛 **Troubleshooting**

### Common Issues

#### 1. **Flags Not Showing**
```typescript
// Check if data is available
console.log('Countries data:', countries);
console.log('Flag emoji:', country.flag_emoji);
```

#### 2. **Missing Flag Field**
- Verify serializer includes `flag_emoji`
- Check API response contains flag data
- Ensure frontend TypeScript types include flag field

#### 3. **Emoji Display Issues**
- Update browser to latest version
- Check system emoji font support
- Consider SVG flag fallbacks for better compatibility

#### 4. **Performance Issues**
- Flags are lightweight Unicode characters
- No additional network requests needed
- Consider lazy loading for large country lists

## 📈 **Future Enhancements**

### Potential Improvements
1. **SVG Flags**: Replace emojis with high-quality SVG flags
2. **Flag Picker**: Admin interface for selecting flags
3. **Regional Flags**: Support for state/province flags
4. **Flag Animations**: Subtle hover effects
5. **Accessibility**: Screen reader support for flag descriptions

### Implementation Ideas
```tsx
// Enhanced flag component with accessibility
<FlagDisplay 
  country={country}
  size="sm"
  showName={true}
  ariaLabel={`${country.name} flag`}
/>
```

---

**Note**: This implementation uses Unicode flag emojis which are supported in all modern browsers and require no additional assets or network requests.
