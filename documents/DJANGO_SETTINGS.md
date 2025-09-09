# Django Project Settings Documentation

## Project Structure
```
v0.0.2/
├── main/                 # Django project settings
│   ├── __init__.py
│   ├── settings.py      # Base settings
│   ├── urls.py          # Main URL configuration
│   ├── wsgi.py          # WSGI configuration
│   └── asgi.py          # ASGI configuration
├── schools/             # Main educational app
│   ├── models/          # Model definitions
│   ├── views/           # View logic
│   ├── admin.py         # Admin interface
│   └── migrations/      # Database migrations
├── user/                # User management app
├── organization/        # Organization management
├── api/                 # REST API endpoints
├── ads/                 # Advertisement system
├── search/              # Search functionality
├── rbac/                # Role-based access control
└── manage.py           # Django management script
```

## Key Settings

### Database Configuration
- **Development**: SQLite (default)
- **Production**: PostgreSQL
- **Migrations**: Always run `python manage.py migrate`

### Installed Apps
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'drf_yasg',
    'schools',
    'user',
    'organization',
    'api',
    'ads',
    'search',
    'rbac',
]
```

### REST Framework Settings
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}
```

### Static Files
- **Development**: Served by Django development server
- **Production**: Collected with `python manage.py collectstatic`

### Media Files
- **Upload Path**: `media/` directory
- **File Storage**: Local file system (development)
- **Production**: Configure for cloud storage

## Environment Variables
```bash
# Required environment variables
DEBUG=True/False
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@host:port/db
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Development Commands
```bash
# Run development server
python manage.py runserver

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Run tests
python manage.py test
```

## API Documentation
- **Swagger UI**: `/swagger/`
- **ReDoc**: `/redoc/`
- **API Root**: `/api/`

## Model Relationships
- **Schools** ↔ **Branches** (One-to-Many)
- **Schools** ↔ **Degrees** (Many-to-Many via SchoolDegreeOffering)
- **Schools** ↔ **Colleges** (Many-to-Many via SchoolCollegeAssociation)
- **Schools** ↔ **Majors** (Many-to-Many via SchoolMajorOffering)
- **Branches** ↔ **Degrees** (Many-to-Many)
- **Branches** ↔ **Colleges** (Many-to-Many)
- **Branches** ↔ **Majors** (Many-to-Many)

## Admin Interface
- **URL**: `/admin/`
- **Models**: All models registered with custom admin classes
- **Features**: Search, filtering, bulk actions, inline editing

## Security Considerations
- **CSRF Protection**: Enabled by default
- **XSS Protection**: Django templates auto-escape
- **SQL Injection**: Django ORM provides protection
- **Authentication**: Session-based with optional token auth

## Performance Optimization
- **Database**: Use select_related() and prefetch_related()
- **Caching**: Configure Redis for production
- **Static Files**: Use CDN in production
- **Database**: Use connection pooling

## Testing
- **Unit Tests**: `python manage.py test`
- **Coverage**: Use coverage.py for test coverage
- **Fixtures**: Use `python manage.py dumpdata` for test data

## Deployment Checklist
- [ ] Set DEBUG=False
- [ ] Configure production database
- [ ] Set up static file serving
- [ ] Configure logging
- [ ] Set up monitoring
- [ ] Configure backup strategy
- [ ] Set up SSL certificates
- [ ] Configure environment variables

## Common Issues
1. **Migration Conflicts**: Delete migrations and recreate
2. **Static Files**: Run collectstatic in production
3. **Database**: Check database permissions
4. **Environment**: Verify environment variables
5. **Dependencies**: Update requirements.txt

## Development Tips
- Use Django Debug Toolbar for development
- Enable SQL logging in development
- Use Django Extensions for additional commands
- Set up pre-commit hooks for code quality
- Use Black for Python code formatting
- Use isort for import sorting 