# Organization Serializer Fix - Field Name Error

## Issue

Error when accessing the organization endpoint:
```
ImproperlyConfigured at /api/v1/organizations/
Field name `industry` is not valid for model `Organization` in `api.serializers.organizations.organization_serializers.OrganizationSerializer`.
```

## Root Cause

The `OrganizationSerializer` was referencing fields that don't exist in the `Organization` model:
- `industry` (singular) - **Does not exist**
- `industry_id` - **Does not exist**

The actual field in the `Organization` model is:
- `industries` (plural) - ManyToManyField

## Model Structure

From `organization/models/base.py`:

```python
class Organization(models.Model):
    """Model representing an organization."""
    uuid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)
    slug = models.SlugField(max_length=75, blank=True)
    logo = models.ImageField(upload_to=organization_logo_image_upload_path, blank=True, null=True)
    name = models.CharField(max_length=100)
    local_name = models.CharField(max_length=250, blank=True, null=True)
    description = models.TextField()
    established_year = models.CharField(max_length=4, null=True, blank=True)
    industries = models.ManyToManyField("Industry", blank=True)  # ✅ Correct field name
    primary_color = models.CharField(default="000000", max_length=25)
    on_primary_color = models.CharField(default="000000", max_length=25)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    self_data = models.CharField(max_length=128, blank=True, db_index=True)
    founders = models.ManyToManyField(Founder, blank=True, related_name='organizations')
```

## Fix Applied

### 1. Removed Invalid Fields from Meta.fields

**Before:**
```python
fields = [
    'uuid',
    'slug',
    'logo',
    'name',
    'local_name',
    'description',
    'established_year',
    'industry',        # ❌ Invalid field
    'industry_id',     # ❌ Invalid field
    'primary_color',
    'on_primary_color',
    'created_at',
    'updated_at',
    'is_active',
    'self_data',
    'founders',
    'founder_ids',
    'industries',      # ✅ Correct field
    'industry_ids',    # ✅ Correct field
]
```

**After:**
```python
fields = [
    'uuid',
    'slug',
    'logo',
    'name',
    'local_name',
    'description',
    'established_year',
    'primary_color',
    'on_primary_color',
    'created_at',
    'updated_at',
    'is_active',
    'self_data',
    'founders',
    'founder_ids',
    'industries',      # ✅ Only this field now
    'industry_ids',
]
```

### 2. Fixed create() Method

**Before:**
```python
def create(self, validated_data):
    industry = validated_data.pop('industry', None)  # ❌ Wrong field
    founders = validated_data.pop('founders', [])
    organization = Organization.objects.create(**validated_data, industry=industry)  # ❌ Wrong field
    if founders:
        organization.founders.set(founders)
    return organization
```

**After:**
```python
def create(self, validated_data):
    industries = validated_data.pop('industries', [])  # ✅ Correct field (plural)
    founders = validated_data.pop('founders', [])
    organization = Organization.objects.create(**validated_data)
    if industries:
        organization.industries.set(industries)  # ✅ Set ManyToMany correctly
    if founders:
        organization.founders.set(founders)
    return organization
```

## Serializer Behavior

### Reading (GET)
```json
{
  "uuid": "...",
  "name": "Example Organization",
  "industries": [  // ✅ Returns full Industry objects
    {
      "uuid": "...",
      "name": "Technology",
      "slug": "technology-..."
    }
  ],
  "founders": [  // ✅ Returns full Founder objects
    {
      "uuid": "...",
      "name": "John Doe",
      "national_name": "..."
    }
  ]
}
```

### Writing (POST/PUT/PATCH)
```json
{
  "name": "New Organization",
  "description": "...",
  "industry_ids": ["uuid1", "uuid2"],  // ✅ Send IDs to link industries
  "founder_ids": ["uuid3", "uuid4"]    // ✅ Send IDs to link founders
}
```

## Files Modified

- `api/serializers/organizations/organization_serializers.py`
  - Removed `'industry'` and `'industry_id'` from fields list
  - Fixed `create()` method to use `industries` instead of `industry`

## Testing

To verify the fix works:

1. **List Organizations:**
   ```bash
   curl http://localhost:8000/api/v1/organizations/
   ```

2. **Create Organization:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/organizations/ \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Test Org",
       "description": "Test description",
       "industry_ids": ["<industry-uuid>"]
     }'
   ```

3. **Retrieve Organization:**
   ```bash
   curl http://localhost:8000/api/v1/organizations/<uuid>/
   ```

## Impact

- ✅ **Fixed**: Organizations endpoint now works correctly
- ✅ **No Breaking Changes**: API structure remains the same (uses `industries` field)
- ✅ **Consistent**: Aligns with actual database model structure
- ✅ **ManyToMany Support**: Properly handles multiple industries per organization

## Related Models

The serializer correctly references:
- `Organization` model (from `organization.models.base`)
- `Industry` model (from `organization.models.base`)
- `Founder` model (from `organization.models.base`)

## Status

✅ **Fixed and Ready**

The organization endpoint should now work without the `ImproperlyConfigured` error.
