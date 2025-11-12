# Why Development Works But Production Fails - EventTicket Migration Issue

## The Mystery

**Production Error:**
```
Field name `quantity_available` is not valid for model `EventTicket`
```

**Development:** No error - everything works fine! 🤔

## The Answer: Database Migration Mismatch

Your development and production databases have **different schemas** due to migration application timing.

### Migration History

#### Migration 0001_initial.py (October 25, 2025)
Created `EventTicket` with **OLD field names**:
```python
EventTicket fields:
- quantity_available  ← Original field
- is_active          ← Original field
- benefits           ← Original field
- sale_start
- sale_end
- display_order
```

#### Migration 0002_remove_eventticket_benefits_and_more.py (October 26, 2025)
**Renamed fields** to match new schema:
```python
REMOVED:
- quantity_available
- is_active
- benefits

ADDED:
- quantity          ← New name for quantity_available
- status           ← Replaces is_active (with choices)
- max_per_order    ← New field
- created_at       ← New field
- updated_at       ← New field
```

## Why Development Works

Your **development database** still has the **OLD schema** from migration 0001:

```
Development Database (db.sqlite3):
event_eventticket table columns:
✅ quantity_available  ← Serializer expects this
✅ is_active          ← Serializer expects this
✅ benefits           ← Serializer expects this
```

**The serializer (before our fix) matched the dev database perfectly!**

## Why Production Fails

Your **production database** has the **NEW schema** from migration 0002:

```
Production Database (PostgreSQL/MySQL):
event_eventticket table columns:
❌ quantity_available  ← DOESN'T EXIST (removed)
❌ is_active          ← DOESN'T EXIST (removed)
❌ benefits           ← DOESN'T EXIST (removed)
✅ quantity           ← EXISTS (new name)
✅ status             ← EXISTS (new field)
✅ max_per_order      ← EXISTS (new field)
```

**The serializer tried to access fields that don't exist in production!**

## How This Happened

1. **Oct 25**: Initial migration created with `quantity_available`
2. **Oct 26**: New migration renamed fields to `quantity`
3. **Production deployed**: Migration 0002 was applied → database updated
4. **Development NOT updated**: Migration 0002 never applied → database still has old schema
5. **Serializer NOT updated**: Still references old field names
6. **Result**: 
   - Development works (old schema + old serializer = match ✅)
   - Production fails (new schema + old serializer = mismatch ❌)

## The Fix We Applied

Updated the serializer to match the **NEW schema** (migration 0002):

```python
# OLD (matches only dev database)
fields = ['quantity_available', 'is_active', 'benefits', ...]

# NEW (matches production database)
fields = ['quantity', 'status', 'max_per_order', ...]
```

## But Wait - Why Does Dev Still Work?

**It shouldn't!** After our serializer fix, development will **BREAK** because:

```
Development database has: quantity_available
Serializer now expects:   quantity
```

## What You Need To Do

### Option 1: Apply Migration in Development (Recommended)

Update your development database to match production:

```bash
cd v0.0.2
python manage.py migrate event
```

This will:
- Remove `quantity_available`, `is_active`, `benefits`
- Add `quantity`, `status`, `max_per_order`
- Now both dev and prod have the same schema ✅

### Option 2: Reset Migrations (Nuclear Option)

If you want a clean slate:

```bash
# WARNING: This deletes all event data!
python manage.py migrate event zero
python manage.py migrate event
```

## Verification Commands

### Check which migrations are applied:
```bash
python manage.py showmigrations event
```

Expected output:
```
event
 [X] 0001_initial
 [X] 0002_remove_eventticket_benefits_and_more  ← Should be checked
```

### Check actual database schema:
```bash
python manage.py dbshell
```

Then in SQL:
```sql
-- SQLite
PRAGMA table_info(event_eventticket);

-- PostgreSQL
\d event_eventticket

-- MySQL
DESCRIBE event_eventticket;
```

Look for these columns:
- ✅ `quantity` (NEW)
- ❌ `quantity_available` (OLD - should NOT exist)

## Best Practices to Prevent This

### 1. Always Apply Migrations in All Environments

```bash
# Development
python manage.py migrate

# Production (before deploying code)
python manage.py migrate
```

### 2. Update Serializers When Renaming Fields

When you rename a model field, update:
- ✅ The model
- ✅ The migration
- ✅ **The serializer** ← Often forgotten!
- ✅ Any API clients/frontend types

### 3. Use Migration Checklist

Before deploying:
```
□ Run migrations in development
□ Update serializers
□ Update frontend types
□ Test API endpoints
□ Run migrations in production
□ Deploy code
```

### 4. Test With Production Database Dump

Periodically:
```bash
# Download production database
pg_dump production_db > prod_dump.sql

# Test locally
psql development_db < prod_dump.sql
python manage.py runserver
# Test all endpoints
```

### 5. Use Django Check Command

```bash
python manage.py check --deploy
```

## Current Status

✅ **Serializer fixed** - Now matches production schema
❌ **Development database** - Still has old schema (needs migration)
✅ **Production database** - Has correct schema

## Action Required

**Run this in development NOW:**
```bash
cd v0.0.2
python manage.py migrate event
```

Then test:
```bash
python manage.py runserver
# Visit http://localhost:8000/api/v1/events/by-slug/your-event-slug/
```

## Summary

| Environment | Database Schema | Serializer (Before Fix) | Result |
|------------|-----------------|-------------------------|---------|
| Development | OLD (quantity_available) | OLD (quantity_available) | ✅ Works |
| Production | NEW (quantity) | OLD (quantity_available) | ❌ Fails |
| Development | OLD (quantity_available) | **NEW (quantity)** | ❌ **Will Fail Now** |
| Production | NEW (quantity) | **NEW (quantity)** | ✅ **Will Work Now** |

**Next Step:** Apply migration 0002 in development to sync schemas!
