# Skill & Language Model Choices Implementation

## Overview

Converted Skill and Language models to use **IntegerChoices** with numeric values instead of text-based choices for better database performance, consistency, and semantic meaning.

**Created**: October 15, 2025  
**Status**: ✅ Complete - Migration Required

---

## Changes Made

### 1. Skill Model

**Before** (No choices):
```python
class Skill(models.Model):
    level = models.CharField(max_length=100, blank=True, verbose_name=_("level"))
```

**After** (IntegerChoices):
```python
class Skill(models.Model):
    class LevelChoices(models.IntegerChoices):
        BEGINNER = 1, _("Beginner")
        INTERMEDIATE = 2, _("Intermediate")
        ADVANCED = 3, _("Advanced")
        EXPERT = 4, _("Expert")

    level = models.IntegerField(
        choices=LevelChoices.choices,
        blank=True,
        null=True,
        verbose_name=_("level"),
        help_text=_("Proficiency level for this skill"),
    )
    
    @property
    def level_display(self):
        """Return the display name of the level"""
        return self.get_level_display() if self.level else ""
```

### 2. Language Model

**Before** (No choices):
```python
class Language(models.Model):
    level = models.CharField(max_length=100, blank=True, verbose_name=_("level"))
```

**After** (IntegerChoices):
```python
class Language(models.Model):
    class ProficiencyChoices(models.IntegerChoices):
        ELEMENTARY = 1, _("Elementary")
        LIMITED_WORKING = 2, _("Limited Working")
        PROFESSIONAL_WORKING = 3, _("Professional Working")
        FULL_PROFESSIONAL = 4, _("Full Professional")
        NATIVE_BILINGUAL = 5, _("Native or Bilingual")

    level = models.IntegerField(
        choices=ProficiencyChoices.choices,
        blank=True,
        null=True,
        verbose_name=_("level"),
        help_text=_("Language proficiency level"),
    )
    
    @property
    def level_display(self):
        """Return the display name of the level"""
        return self.get_level_display() if self.level else ""
```

---

## Benefits of IntegerChoices

### 1. **Database Efficiency**
- ✅ Stores integers (4 bytes) instead of strings (variable length)
- ✅ Faster queries and comparisons
- ✅ More efficient indexes

### 2. **Semantic Meaning**
- ✅ Numbers represent progression: 1 → 2 → 3 → 4
- ✅ Easy to query: `level__gte=3` (Advanced or higher)
- ✅ Sortable by proficiency level

### 3. **Type Safety**
- ✅ Django validates values automatically
- ✅ IDE autocomplete for choice values
- ✅ Better error messages

### 4. **Internationalization**
- ✅ Labels can be translated without changing stored values
- ✅ Display names independent from database values

### 5. **Data Integrity**
- ✅ Only valid values can be stored
- ✅ Prevents typos and inconsistent data
- ✅ Clear contract between frontend and backend

---

## Skill Level Mapping

| Value | Constant | Display Name | Description |
|-------|----------|--------------|-------------|
| 1 | `BEGINNER` | Beginner | Just starting to learn |
| 2 | `INTERMEDIATE` | Intermediate | Comfortable with basics |
| 3 | `ADVANCED` | Advanced | Proficient, can work independently |
| 4 | `EXPERT` | Expert | Master level, can teach others |

### Usage Examples

```python
# Create skill with level
skill = Skill.objects.create(
    user=profile,
    name="Python",
    level=Skill.LevelChoices.ADVANCED  # Stores: 3
)

# Get display name
print(skill.get_level_display())  # Output: "Advanced"
print(skill.level_display)  # Property: "Advanced"

# Query by level
advanced_skills = Skill.objects.filter(level__gte=3)  # Advanced and Expert
expert_skills = Skill.objects.filter(level=Skill.LevelChoices.EXPERT)

# Check level
if skill.level == Skill.LevelChoices.BEGINNER:
    print("Still learning!")
```

---

## Language Proficiency Mapping

| Value | Constant | Display Name | Description |
|-------|----------|--------------|-------------|
| 1 | `ELEMENTARY` | Elementary | Basic words and phrases |
| 2 | `LIMITED_WORKING` | Limited Working | Can have simple conversations |
| 3 | `PROFESSIONAL_WORKING` | Professional Working | Can work professionally |
| 4 | `FULL_PROFESSIONAL` | Full Professional | Near-native fluency |
| 5 | `NATIVE_BILINGUAL` | Native/Bilingual | Native or bilingual proficiency |

### Usage Examples

```python
# Create language with level
language = Language.objects.create(
    user=profile,
    name="Spanish",
    level=Language.ProficiencyChoices.PROFESSIONAL_WORKING,  # Stores: 3
    is_native=False
)

# Get display name
print(language.get_level_display())  # Output: "Professional Working"
print(language.level_display)  # Property: "Professional Working"

# Query by level
fluent_languages = Language.objects.filter(level__gte=4)  # Full Professional or Native
native_or_bilingual = Language.objects.filter(
    level=Language.ProficiencyChoices.NATIVE_BILINGUAL
)
```

---

## Migration Required

### Step 1: Create Migration

```bash
cd v0.0.2
python manage.py makemigrations user
```

**Expected Output**:
```
Migrations for 'user':
  user/migrations/0XXX_alter_skill_level_alter_language_level.py
    - Alter field level on skill
    - Alter field level on language
```

### Step 2: Handle Existing Data

The migration will need to convert existing string values to integers. Create a data migration:

```python
# user/migrations/0XXX_convert_skill_language_levels.py
from django.db import migrations

def convert_skill_levels(apps, schema_editor):
    Skill = apps.get_model('user', 'Skill')
    
    level_mapping = {
        'Beginner': 1,
        'Intermediate': 2,
        'Advanced': 3,
        'Expert': 4,
        '': None,  # Empty string to None
    }
    
    for skill in Skill.objects.all():
        if skill.level in level_mapping:
            skill.level = level_mapping[skill.level]
            skill.save(update_fields=['level'])

def convert_language_levels(apps, schema_editor):
    Language = apps.get_model('user', 'Language')
    
    level_mapping = {
        'Elementary': 1,
        'Limited Working': 2,
        'Professional Working': 3,
        'Full Professional': 4,
        'Native/Bilingual': 5,
        '': None,  # Empty string to None
    }
    
    for language in Language.objects.all():
        if language.level in level_mapping:
            language.level = level_mapping[language.level]
            language.save(update_fields=['level'])

class Migration(migrations.Migration):
    dependencies = [
        ('user', '0XXX_previous_migration'),
    ]

    operations = [
        migrations.RunPython(convert_skill_levels, migrations.RunPython.noop),
        migrations.RunPython(convert_language_levels, migrations.RunPython.noop),
    ]
```

### Step 3: Apply Migrations

```bash
python manage.py migrate user
```

---

## API/Serializer Updates Needed

### Skill Serializer

Update to handle both input (display names) and output (integers):

```python
# api/serializers/resume_serializers.py

class SkillSerializer(serializers.ModelSerializer):
    level = serializers.IntegerField(allow_null=True, required=False)
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    
    class Meta:
        model = Skill
        fields = ['id', 'name', 'level', 'level_display', 'attachments']
    
    def validate_level(self, value):
        """Validate level is a valid choice"""
        if value is not None and value not in [1, 2, 3, 4]:
            raise serializers.ValidationError("Invalid skill level")
        return value
```

### Language Serializer

```python
class LanguageSerializer(serializers.ModelSerializer):
    level = serializers.IntegerField(allow_null=True, required=False)
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    
    class Meta:
        model = Language
        fields = ['id', 'name', 'level', 'level_display', 'is_native', 'attachments']
    
    def validate_level(self, value):
        """Validate level is a valid choice"""
        if value is not None and value not in [1, 2, 3, 4, 5]:
            raise serializers.ValidationError("Invalid language proficiency level")
        return value
```

---

## Frontend Updates Needed

### Update Skill Types

```typescript
// src/modules/resume/types.ts

export interface Skill {
  id: number;
  name: string;
  level: number | null;  // Changed from string
  level_display?: string;  // Add display field
  attachments: Attachment[];
  attachment_ids?: number[];
}

export const SKILL_LEVELS = {
  BEGINNER: 1,
  INTERMEDIATE: 2,
  ADVANCED: 3,
  EXPERT: 4,
} as const;

export const SKILL_LEVEL_LABELS: Record<number, string> = {
  1: "Beginner",
  2: "Intermediate",
  3: "Advanced",
  4: "Expert",
};
```

### Update Skill Form

```typescript
// src/modules/resume/ui/components/skill-form.tsx

const SKILL_LEVELS = [
  { value: 0, label: "Not specified" },  // Use 0 for unspecified
  { value: 1, label: "Beginner" },
  { value: 2, label: "Intermediate" },
  { value: 3, label: "Advanced" },
  { value: 4, label: "Expert" },
];

// Update schema
export const skillInputSchema = z.object({
  name: z.string().min(1, "Skill name is required").max(100),
  level: z.number().int().min(1).max(4).nullable().optional(),
  attachment_ids: z.array(z.number()).optional(),
});

// Update form submission
const handleFormSubmit = (data: SkillInput) => {
  const submitData: SkillInput = {
    ...data,
    level: data.level === 0 ? null : data.level,  // Convert 0 to null
    attachment_ids: uploadedAttachmentIds.length > 0 ? uploadedAttachmentIds : undefined,
  };
  onSubmit(submitData);
};
```

### Update Skill Section Display

```typescript
// src/modules/resume/ui/components/skill-section.tsx

{skill.level && (
  <p className="text-sm text-muted-foreground mb-2">
    Level: <span className="font-medium">{skill.level_display}</span>
  </p>
)}
```

---

## Testing Checklist

### Backend Tests

- [ ] Create skill with level=1 (Beginner)
- [ ] Create skill with level=None (no level)
- [ ] Update skill level from 2 to 3
- [ ] Query skills with level >= 3 (Advanced or Expert)
- [ ] Verify get_level_display() returns correct string
- [ ] Verify level_display property works
- [ ] Test API returns level as integer
- [ ] Test API returns level_display as string

### Frontend Tests

- [ ] Dropdown shows numeric values internally
- [ ] Dropdown displays text labels to user
- [ ] "Not specified" converts to null on submit
- [ ] Edit skill shows correct level selected
- [ ] Skill display shows level_display text
- [ ] API requests send integers
- [ ] API responses handle integers

### Migration Tests

- [ ] Run migration on test database
- [ ] Verify existing "Beginner" → 1
- [ ] Verify existing "Intermediate" → 2
- [ ] Verify existing "Advanced" → 3
- [ ] Verify existing "Expert" → 4
- [ ] Verify empty strings → null
- [ ] Verify no data loss

---

## Rollback Plan

If issues arise, rollback steps:

1. **Revert code changes**:
   ```bash
   git revert <commit-hash>
   ```

2. **Rollback migrations**:
   ```bash
   python manage.py migrate user 0XXX_previous_migration
   ```

3. **Delete migration files**:
   ```bash
   rm user/migrations/0XXX_alter_skill_level*.py
   rm user/migrations/0XXX_convert_skill_language*.py
   ```

---

## Performance Impact

### Database Query Performance

**Before** (VARCHAR):
```sql
SELECT * FROM user_skill WHERE level = 'Advanced';  -- String comparison
```

**After** (INTEGER):
```sql
SELECT * FROM user_skill WHERE level = 3;  -- Integer comparison (faster)
```

### Index Performance

- ✅ Integer indexes are more efficient
- ✅ Range queries are faster: `level >= 3`
- ✅ Sorting by level is more meaningful

### Storage Impact

- ✅ Reduced storage per row (4 bytes vs variable)
- ✅ Better cache utilization
- ✅ Faster table scans

---

## Related Documentation

- Skills Section Implementation: `docs/SKILLS_SECTION_IMPLEMENTATION.md`
- Skills Select Fix: `docs/SKILLS_SELECT_EMPTY_VALUE_FIX.md`
- Django Choices: https://docs.djangoproject.com/en/stable/ref/models/fields/#choices

---

## Summary

### What Changed
- ✅ Skill.level: CharField → IntegerField with IntegerChoices
- ✅ Language.level: CharField → IntegerField with IntegerChoices
- ✅ Added level_display property to both models
- ✅ Numeric values (1-4 for skills, 1-5 for languages)

### Why
- ✅ Better database performance
- ✅ Semantic meaning (progression)
- ✅ Type safety and validation
- ✅ Consistent with Django best practices

### Next Steps
1. Create and apply migrations
2. Update API serializers
3. Update frontend types and forms
4. Test thoroughly
5. Update documentation

---

**Status**: ✅ Code Complete - Migration Pending  
**Impact**: Medium (requires migration + frontend updates)  
**Risk**: Low (backward compatible with data migration)
