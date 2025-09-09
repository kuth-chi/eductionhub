# School Address Improvement Documentation

## Overview

This document outlines the improvements made to the school address system, enhancing the user experience with better address fields and Geo relationships.

## Features

### ✅ Enhanced Address Fields

- **Street Address**: Primary address line (required)
- **Address Line 2**: Secondary address line (optional)
- **Box Number**: P.O. Box or mailbox number (optional)
- **Postal Code**: ZIP code or postal code (required)

### ✅ Geo Relationships

- **Country**: Dropdown with all countries from Geo system
- **State/Province**: Cascading dropdown based on selected country
- **City**: Cascading dropdown based on selected state
- **Village/Suburb**: Cascading dropdown based on selected city

### ✅ Improved UX

- **Cascading Dropdowns**: Selections automatically filter dependent options
- **Loading States**: Clear indicators while fetching data
- **Form Validation**: Proper validation for required fields
- **Responsive Design**: Works on mobile and desktop
- **Professional Icons**: Uses Lucide icons for consistent design

## Backend Changes

### Database Schema Updates

#### School Model (`schools/models/schoolsModel.py`)

```python
# New address fields
street_address = models.CharField(max_length=255, blank=True, verbose_name=_("street address"))
address_line_2 = models.CharField(max_length=255, blank=True, verbose_name=_("address line 2"))
box_number = models.CharField(max_length=50, blank=True, verbose_name=_("box number"))
postal_code = models.CharField(max_length=20, blank=True, verbose_name=_("postal code"))

# Geo relationships
country = models.ForeignKey("geo.Country", on_delete=models.SET_NULL, null=True, blank=True, related_name="schools")
state = models.ForeignKey("geo.State", on_delete=models.SET_NULL, null=True, blank=True, related_name="schools")
city = models.ForeignKey("geo.City", on_delete=models.SET_NULL, null=True, blank=True, related_name="schools")
village = models.ForeignKey("geo.Village", on_delete=models.SET_NULL, null=True, blank=True, related_name="schools")
```

#### Migration (`schools/migrations/0013_add_school_address_fields.py`)

- Adds new address fields to School model
- Creates foreign key relationships to Geo models
- Maintains backward compatibility

### API Updates

#### School Serializer (`api/serializers/schools/base.py`)

```python
class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = (
            # ... existing fields ...
            "street_address",
            "address_line_2", 
            "box_number",
            "postal_code",
            "country",
            "state", 
            "city",
            "village",
            "location",  # Legacy field
            # ... rest of fields ...
        )
```

## Frontend Changes

### Schema Updates (`web/src/modules/schools/schemas.ts`)

```typescript
export const schoolCreationSchema = z.object({
  // ... existing fields ...
  
  // Address fields
  street_address: z.string().optional(),
  address_line_2: z.string().optional(),
  box_number: z.string().optional(),
  postal_code: z.string().optional(),
  
  // Location fields using Geo relationships
  country: z.object({ id: z.number().optional(), name: z.string().optional() }).optional(),
  state: z.object({ id: z.number().optional(), name: z.string().optional() }).optional(),
  city: z.object({ id: z.number().optional(), name: z.string().optional() }).optional(),
  village: z.object({ id: z.number().optional(), name: z.string().optional() }).optional(),
});
```

### Location Form Component (`web/src/modules/schools/ui/components/location-form.tsx`)

#### Features

- **Cascading Dropdowns**: Country → State → City → Village
- **Real-time Updates**: Automatically loads dependent options
- **Loading States**: Shows loading indicators
- **Form Integration**: Uses React Hook Form context
- **Error Handling**: Graceful error handling for API failures

#### Usage

```typescript
import { LocationForm } from '@/modules/schools/ui/components/location-form';

// In your form component
<LocationForm />
```

## Data Flow

### 1. Form Submission

```typescript
{
  street_address: "123 Main Street",
  address_line_2: "Suite 100",
  box_number: "P.O. Box 456",
  postal_code: "12345",
  country: { id: 1, name: "United States" },
  state: { id: 5, name: "California" },
  city: { id: 15, name: "Los Angeles" },
  village: { id: 45, name: "Downtown" }
}
```

### 2. API Processing

- Frontend sends structured data to backend
- Backend validates and saves to database
- Geo relationships are properly linked
- Legacy `location` field maintained for compatibility

### 3. Data Retrieval

- API returns complete address information
- Geo relationships include full location hierarchy
- Frontend displays formatted address

## Implementation Steps

### Backend Setup

1. **Run Migration**:

   ```bash
   cd v0.0.2
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Verify Geo Data**:

   ```bash
   python manage.py check_levels
   python manage.py check_school_types
   ```

### Frontend Setup

1. **Update Environment**:

   ```bash
   # In web/.env.local
   NEXT_PUBLIC_BACKEND_API_URL=http://localhost:8000
   ```

2. **Test Location Form**:
   - Visit `/test-form-debug` to test location functionality
   - Check browser console for API logs

### Integration

1. **Add to School Creation Flow**:

   ```typescript
   import { LocationForm } from '@/modules/schools/ui/components/location-form';
   
   // In your multi-step form Step 2
   <LocationForm />
   ```

2. **Updated Step 2 Address Form**:
   - Enhanced `SchoolAddressForm` component now includes:
     - Street address, address line 2, box number, postal code
     - Cascading location dropdowns (Country → State → City → Village)
     - Map coordinates integration
     - Proper form validation

2. **Update Form Validation**:
   - Ensure required fields are validated
   - Add custom validation rules as needed

## Benefits

### ✅ Data Consistency

- Uses centralized Geo data
- Prevents invalid location combinations
- Maintains data integrity

### ✅ User Experience

- Intuitive cascading dropdowns
- Clear loading indicators
- Responsive design
- Form validation

### ✅ Maintainability

- Centralized location management
- Easy to extend with new fields
- Backward compatibility
- Clear documentation

### ✅ Scalability

- Easy to add new location levels
- Supports international addresses
- Flexible field structure

## Testing

### Backend Testing

```bash
# Test migrations
python manage.py migrate --plan

# Test API endpoints
curl http://localhost:8000/api/v1/schools/
curl http://localhost:8000/api/v1/countries/
curl http://localhost:8000/api/v1/states/
```

### Frontend Testing

```bash
# Test location form
npm run dev
# Visit: http://localhost:3000/test-form-debug
```

### API Testing

```bash
# Test Geo API
curl http://localhost:8000/api/v1/countries/
curl http://localhost:8000/api/v1/states/by_country/?country_id=1
curl http://localhost:8000/api/v1/cities/by_state/?state_id=5
```

## Troubleshooting

### Common Issues

1. **Migration Errors**:
   - Ensure Geo app is installed
   - Check dependencies in migration file
   - Run `python manage.py showmigrations`

2. **API Connection Issues**:
   - Verify `NEXT_PUBLIC_BACKEND_API_URL` is set
   - Check Django server is running
   - Test API endpoints directly

3. **Form Validation Errors**:
   - Check schema definitions
   - Verify field names match backend
   - Test with minimal data

### Debug Tools

- **Browser Console**: Check for API logs
- **Django Admin**: Verify data in database

## Future Enhancements

### Potential Improvements

1. **Address Validation**: Integrate with postal service APIs
2. **Auto-complete**: Add address suggestion features
3. **Map Integration**: Add location picker with maps
4. **International Support**: Add country-specific address formats
5. **Bulk Import**: Support CSV import with address data

### Extensibility

- Easy to add new address fields
- Flexible Geo relationship structure
- Modular component design
- Clear separation of concerns

## Support

For issues or questions:

1. Check this documentation
2. Review API logs
3. Test with debug pages
4. Check database migrations
5. Verify environment configuration
