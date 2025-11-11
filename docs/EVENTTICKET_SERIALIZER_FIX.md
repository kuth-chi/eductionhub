# EventTicket Serializer Field Mismatch Fix

## Problem Description

Production environment was experiencing `ImproperlyConfigured` errors when accessing event detail pages:

```
django.core.exceptions.ImproperlyConfigured: Field name `quantity_available` is not valid for model `EventTicket` in `api.serializers.event.financial_serializers.EventTicketSerializer`.
```

## Root Cause

The `EventTicketSerializer` in `api/serializers/event/financial_serializers.py` was referencing fields that don't exist in the `EventTicket` model:

**Serializer was using:**
- `quantity_available` (doesn't exist)
- `is_active` (doesn't exist)
- `benefits` (doesn't exist)

**Model actually has:**
- `quantity` (actual field name)
- `status` (instead of is_active)
- No benefits field

## Solution

Updated the `EventTicketSerializer` to match the actual `EventTicket` model fields defined in `event/models/financial.py`.

### Changes Made

**Before:**
```python
class Meta:
    model = EventTicket
    fields = [
        'id', 'event', 'name', 'description', 'price', 'currency',
        'quantity_available', 'quantity_sold', 'remaining',  # ❌ Wrong field name
        'sale_start', 'sale_end', 'is_active', 'is_available',  # ❌ is_active doesn't exist
        'display_order', 'benefits'  # ❌ benefits doesn't exist
    ]

def get_remaining(self, obj):
    if obj.quantity_available is None:  # ❌ Wrong field name
        return None
    return max(0, obj.quantity_available - obj.quantity_sold)
```

**After:**
```python
class Meta:
    model = EventTicket
    fields = [
        'id', 'event', 'name', 'description', 'price', 'currency',
        'quantity', 'quantity_sold', 'remaining',  # ✅ Correct field name
        'sale_start', 'sale_end', 'status', 'is_available',  # ✅ Use status field
        'display_order', 'max_per_order'  # ✅ Use max_per_order instead of benefits
    ]

def get_remaining(self, obj):
    if obj.quantity is None:  # ✅ Correct field name
        return None
    return max(0, obj.quantity - obj.quantity_sold)
```

## EventTicket Model Fields Reference

From `event/models/financial.py`, the actual EventTicket model has:

### Database Fields:
- `id` - Primary key
- `event` - ForeignKey to Event
- `name` - CharField (ticket name)
- `description` - TextField
- `price` - DecimalField
- `currency` - CharField (default: 'USD')
- `quantity` - IntegerField (total available)
- `quantity_sold` - IntegerField (default: 0)
- `max_per_order` - IntegerField (default: 10)
- `sale_start` - DateTimeField (nullable)
- `sale_end` - DateTimeField (nullable)
- `status` - CharField (choices: active, sold-out, expired, inactive)
- `display_order` - IntegerField (default: 0)
- `created_at` - DateTimeField (auto_now_add)
- `updated_at` - DateTimeField (auto_now)

### Computed Properties:
- `is_available` - Property that checks if ticket is currently purchasable
- `remaining_quantity` - Property that calculates tickets left

## Why This Error Only Appeared in Production

Development and production databases had different schemas:
- **Development**: Likely had an older migration with `quantity_available` field
- **Production**: Had the current schema with `quantity` field

This type of mismatch typically occurs when:
1. Database migrations aren't synchronized between environments
2. Model changes were made but serializers weren't updated
3. Direct database changes were made in production

## Testing Checklist

- [x] Serializer matches model field names
- [x] No references to `quantity_available` in codebase
- [x] No references to `is_active` (using `status` instead)
- [x] No references to `benefits` field
- [ ] Test event detail API endpoint: `/api/v1/events/by-slug/{slug}/`
- [ ] Verify ticket information displays correctly in frontend
- [ ] Test ticket purchase flow if implemented

## Deployment Steps

### Backend Deployment

1. **Commit the changes:**
   ```bash
   cd v0.0.2
   git add api/serializers/event/financial_serializers.py
   git commit -m "Fix EventTicket serializer field mismatch"
   git push origin main
   ```

2. **Deploy to production:**
   ```bash
   # SSH into production server
   cd /path/to/backend
   git pull origin main
   
   # Restart Django application
   sudo systemctl restart gunicorn
   # or
   pm2 restart django-backend
   ```

3. **Verify the fix:**
   ```bash
   # Check logs for any errors
   tail -f /var/log/django/error.log
   
   # Test the endpoint
   curl https://authz.educationhub.io/api/v1/events/by-slug/fundraising-for-education-material/
   ```

### Frontend (No Changes Required)

The frontend already expects the correct field names based on the TypeScript types. No frontend changes are needed.

## Prevention

To prevent similar issues in the future:

1. **Always update serializers when changing models**
2. **Run migrations consistently across all environments**
3. **Use automated tests to catch serializer/model mismatches:**
   ```python
   def test_ticket_serializer_fields_match_model():
       """Ensure serializer fields exist in model"""
       from event.models import EventTicket
       from api.serializers.event.financial_serializers import EventTicketSerializer
       
       model_fields = {f.name for f in EventTicket._meta.get_fields()}
       serializer_fields = set(EventTicketSerializer.Meta.fields)
       
       # Remove computed/read-only fields
       serializer_fields.discard('remaining')
       serializer_fields.discard('is_available')
       
       for field in serializer_fields:
           assert field in model_fields, f"Field '{field}' not in model"
   ```

4. **Document model changes in migration files**
5. **Use database schema comparison tools before deployment**

## Related Files

- **Model**: `event/models/financial.py` - EventTicket model definition
- **Serializer**: `api/serializers/event/financial_serializers.py` - EventTicketSerializer
- **Viewset**: `api/views/events_viewset.py` - Events API endpoint
- **Frontend Types**: `web_frontend/web/src/modules/events/types.ts` - TypeScript definitions

## Related Issues

This fix resolves the production error:
```
Internal Server Error: /api/v1/events/by-slug/{slug}/
Field name `quantity_available` is not valid for model `EventTicket`
```

After this fix, event detail pages should load correctly in production with full ticket information displayed.
