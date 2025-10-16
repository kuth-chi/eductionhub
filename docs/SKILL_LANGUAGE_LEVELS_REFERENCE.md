# Quick Reference: Skill & Language Level Values

## Skill Levels (1-4)

| Integer | Constant | Display | Use When |
|---------|----------|---------|----------|
| `null` | - | Not specified | User hasn't selected a level |
| `1` | `BEGINNER` | Beginner | Just starting to learn |
| `2` | `INTERMEDIATE` | Intermediate | Comfortable with basics |
| `3` | `ADVANCED` | Advanced | Can work independently |
| `4` | `EXPERT` | Expert | Master level |

### Python Examples
```python
from user.models import Skill

# Create
Skill.objects.create(name="Python", level=Skill.LevelChoices.ADVANCED)

# Query
advanced_skills = Skill.objects.filter(level__gte=3)
expert_skills = Skill.objects.filter(level=Skill.LevelChoices.EXPERT)

# Display
skill.get_level_display()  # Returns: "Advanced"
skill.level_display  # Property: "Advanced"
```

---

## Language Proficiency Levels (1-5)

| Integer | Constant | Display | CEFR Equivalent | Use When |
|---------|----------|---------|-----------------|----------|
| `null` | - | Not specified | - | User hasn't selected |
| `1` | `ELEMENTARY` | Elementary | A1-A2 | Basic phrases |
| `2` | `LIMITED_WORKING` | Limited Working | B1 | Simple conversations |
| `3` | `PROFESSIONAL_WORKING` | Professional Working | B2-C1 | Work professionally |
| `4` | `FULL_PROFESSIONAL` | Full Professional | C2 | Near-native |
| `5` | `NATIVE_BILINGUAL` | Native/Bilingual | Native | Native speaker |

### Python Examples
```python
from user.models import Language

# Create
Language.objects.create(
    name="Spanish", 
    level=Language.ProficiencyChoices.PROFESSIONAL_WORKING
)

# Query
fluent = Language.objects.filter(level__gte=4)
native = Language.objects.filter(level=Language.ProficiencyChoices.NATIVE_BILINGUAL)

# Display
language.get_level_display()  # Returns: "Professional Working"
language.level_display  # Property: "Professional Working"
```

---

## TypeScript/Frontend Constants

```typescript
// Skill Levels
export const SKILL_LEVELS = {
  NOT_SPECIFIED: null,
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

// Language Levels
export const LANGUAGE_LEVELS = {
  NOT_SPECIFIED: null,
  ELEMENTARY: 1,
  LIMITED_WORKING: 2,
  PROFESSIONAL_WORKING: 3,
  FULL_PROFESSIONAL: 4,
  NATIVE_BILINGUAL: 5,
} as const;

export const LANGUAGE_LEVEL_LABELS: Record<number, string> = {
  1: "Elementary",
  2: "Limited Working",
  3: "Professional Working",
  4: "Full Professional",
  5: "Native/Bilingual",
};
```

---

## API Request/Response Examples

### Create Skill
```json
POST /api/v1/user-skills/
{
  "name": "JavaScript",
  "level": 3,
  "attachment_ids": [123, 124]
}
```

### Response
```json
{
  "id": 456,
  "name": "JavaScript",
  "level": 3,
  "level_display": "Advanced",
  "attachments": [...]
}
```

### Create Language
```json
POST /api/v1/user-languages/
{
  "name": "French",
  "level": 4,
  "is_native": false,
  "attachment_ids": [125]
}
```

### Response
```json
{
  "id": 789,
  "name": "French",
  "level": 4,
  "level_display": "Full Professional",
  "is_native": false,
  "attachments": [...]
}
```

---

## Database Queries

### Skills by Level
```python
# All skills
all_skills = Skill.objects.all()

# Only specified levels
specified = Skill.objects.exclude(level__isnull=True)

# By exact level
beginners = Skill.objects.filter(level=1)
experts = Skill.objects.filter(level=4)

# By range
intermediate_plus = Skill.objects.filter(level__gte=2)
advanced_or_expert = Skill.objects.filter(level__in=[3, 4])

# Order by level
ordered = Skill.objects.order_by('-level', 'name')
```

### Languages by Level
```python
# Native or bilingual only
native = Language.objects.filter(level=5)

# Professional levels (3+)
professional = Language.objects.filter(level__gte=3)

# Not native but fluent
fluent_non_native = Language.objects.filter(level__gte=4, is_native=False)

# Order by proficiency
ordered = Language.objects.order_by('-level', 'name')
```

---

## Validation

### Django Model Validation
```python
from django.core.exceptions import ValidationError

def validate_skill_level(value):
    if value is not None and value not in [1, 2, 3, 4]:
        raise ValidationError(f"{value} is not a valid skill level")

def validate_language_level(value):
    if value is not None and value not in [1, 2, 3, 4, 5]:
        raise ValidationError(f"{value} is not a valid language level")
```

### DRF Serializer Validation
```python
class SkillSerializer(serializers.ModelSerializer):
    def validate_level(self, value):
        if value is not None and value not in [1, 2, 3, 4]:
            raise serializers.ValidationError("Invalid skill level")
        return value
```

### Frontend Validation (Zod)
```typescript
const skillSchema = z.object({
  name: z.string().min(1).max(100),
  level: z.number().int().min(1).max(4).nullable().optional(),
});

const languageSchema = z.object({
  name: z.string().min(1).max(100),
  level: z.number().int().min(1).max(5).nullable().optional(),
});
```

---

## Migration Commands

```bash
# Create migration
python manage.py makemigrations user

# Show SQL (optional)
python manage.py sqlmigrate user 0XXX

# Apply migration
python manage.py migrate user

# Check status
python manage.py showmigrations user
```

---

## Common Patterns

### Setting Default Level
```python
# In form or admin
skill = Skill(name="New Skill", level=Skill.LevelChoices.BEGINNER)
```

### Conditional Display
```python
# In template or serializer
level_text = skill.level_display if skill.level else "Not specified"
```

### Filtering for Resume
```python
# Show only skills with intermediate or higher
resume_skills = Skill.objects.filter(
    user=user,
    level__gte=Skill.LevelChoices.INTERMEDIATE
)
```

### Progress Tracking
```python
# Calculate average skill level
from django.db.models import Avg
avg_level = Skill.objects.filter(user=user).aggregate(Avg('level'))
```

---

**Last Updated**: October 15, 2025  
**Related**: `SKILL_LANGUAGE_CHOICES_IMPLEMENTATION.md`
