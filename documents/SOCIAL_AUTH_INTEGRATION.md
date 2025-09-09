# Social Authentication Integration with dj-rest-auth

This document describes the complete integration of social authentication using dj-rest-auth with Django Allauth for Google, Facebook, and Telegram providers.

## Overview

The system now supports:
- **Regular Authentication**: Username/password login with JWT tokens
- **Social Authentication**: Google, Facebook, and Telegram login via dj-rest-auth
- **Unified JWT Response**: Both authentication methods return identical JWT token structure
- **Profile Integration**: Automatic profile creation and data population
- **Frontend Integration**: Seamless integration with Next.js frontend

## Architecture

### Backend Components

1. **dj-rest-auth Integration**: Provides REST API endpoints for social authentication
2. **Custom Social Views**: Enhanced social login views with JWT token generation
3. **Custom Serializers**: Profile and user data serialization
4. **Allauth Adapters**: Handle social account creation and user data population

### Authentication Flow

```
Frontend → Social Provider → Django Allauth → dj-rest-auth → Custom Views → JWT Tokens
```

## API Endpoints

### Authentication Endpoints

| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/api/v1/auth/login/` | POST | Regular username/password login | JWT tokens + user data |
| `/api/v1/auth/logout/` | POST | Logout (blacklist tokens) | Success message |
| `/api/v1/auth/password/reset/` | POST | Password reset | Success message |
| `/api/v1/auth/password/reset/confirm/` | POST | Confirm password reset | Success message |
| `/api/v1/auth/password/change/` | POST | Change password | Success message |
| `/api/v1/auth/user/` | GET/PUT/PATCH | Get/update user details | User data |

### Registration Endpoints

| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/api/v1/auth/registration/` | POST | User registration | JWT tokens + user data |
| `/api/v1/auth/registration/verify-email/` | POST | Verify email | Success message |
| `/api/v1/auth/registration/resend-email/` | POST | Resend verification email | Success message |

### Social Authentication Endpoints

| Endpoint | Method | Description | Provider |
|----------|--------|-------------|----------|
| `/api/v1/auth/google/` | POST | Google OAuth2 login | Google |
| `/api/v1/auth/facebook/` | POST | Facebook OAuth2 login | Facebook |
| `/api/v1/auth/telegram/` | POST | Telegram login | Telegram |

### Custom Endpoints (Legacy Support)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/token/` | POST | Direct JWT token generation |
| `/api/v1/token/refresh/` | POST | Refresh JWT tokens |
| `/api/v1/auth-status/` | GET | Check authentication status |
| `/api/v1/active-sessions/` | GET | List active sessions |

## Frontend Integration

### Social Login Usage

```typescript
// For Google Login
const googleLogin = async (accessToken: string) => {
  const response = await fetch('/api/v1/auth/google/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      access_token: accessToken, // From Google OAuth2
    }),
  });
  
  const data = await response.json();
  // data contains: access, refresh, user, profile
};

// For Facebook Login
const facebookLogin = async (accessToken: string) => {
  const response = await fetch('/api/v1/auth/facebook/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      access_token: accessToken, // From Facebook OAuth2
    }),
  });
  
  const data = await response.json();
};

// For Telegram Login
const telegramLogin = async (telegramData: any) => {
  const response = await fetch('/api/v1/auth/telegram/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(telegramData), // Telegram widget data
  });
  
  const data = await response.json();
};
```

### Response Format

All authentication endpoints return the same format:

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_staff": false,
    "is_superuser": false
  },
  "profile": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "photo": "/media/profiles/photo.jpg",
    "gender": "male",
    "occupation": "student",
    "timezone": "UTC",
    "is_active": true,
    "last_login": "2024-01-01T12:00:00Z"
  }
}
```

## Environment Variables

Add these to your `.env` file:

```bash
# Google OAuth2
GOOGLE_AUTH_CLIENT_ID=your_google_client_id
GOOGLE_AUTH_SECRET=your_google_client_secret

# Facebook OAuth2
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret

# Telegram Bot
TELEGRAM_BOT_ID=your_telegram_bot_id
TELEGRAM_LOGIN_PUBLIC_KEY=your_telegram_public_key

# Frontend URL for redirects
WEB_CLIENT_URL=http://localhost:3000
```

## Configuration

### Settings Configuration

The following settings are configured in `main/settings.py`:

```python
# dj-rest-auth configuration
REST_AUTH = {
    'USE_JWT': True,
    'JWT_AUTH_COOKIE': 'access_token',
    'JWT_AUTH_REFRESH_COOKIE': 'refresh_token',
    'JWT_AUTH_HTTPONLY': True,
    'JWT_AUTH_SECURE': not DEBUG,
    'JWT_AUTH_SAMESITE': 'Lax',
    'USER_DETAILS_SERIALIZER': 'api.serializers.user_details.UserDetailsSerializer',
    'JWT_SERIALIZER': 'api.serializers.custom_jwt.CustomTokenObtainPairSerializer',
    'REGISTER_SERIALIZER': 'api.serializers.registration.CustomRegisterSerializer',
}

# Social account providers
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email', 'openid'],
        'APP': {
            'client_id': os.getenv('GOOGLE_AUTH_CLIENT_ID'),
            'secret': os.getenv('GOOGLE_AUTH_SECRET'),
        },
        'AUTH_PARAMS': {'access_type': 'online'},
    },
    'facebook': {
        'METHOD': 'oauth2',
        'SCOPE': ['email', 'public_profile'],
        'FIELDS': ['id', 'first_name', 'last_name', 'name', 'email', 'picture'],
        'EXCHANGE_TOKEN': True,
        'VERSION': 'v13.0',
    },
    'telegram': {
        'APP': {
            'client_id': TELEGRAM_BOT_ID,
            'secret': TELEGRAM_LOGIN_PUBLIC_KEY,
        },
    },
}
```

## Security Features

1. **JWT Token Security**: Uses RS256 algorithm with public/private key pair
2. **Cookie Security**: HTTPOnly, Secure, SameSite attributes
3. **CORS Configuration**: Proper CORS setup for frontend integration
4. **Token Validation**: Comprehensive token validation and sanitization
5. **Session Management**: Automatic session cleanup and token blacklisting

## Testing

### Test Regular Authentication

```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'
```

### Test Google Authentication

```bash
curl -X POST http://localhost:8000/api/v1/auth/google/ \
  -H "Content-Type: application/json" \
  -d '{"access_token": "google_access_token_here"}'
```

### Test User Details

```bash
curl -X GET http://localhost:8000/api/v1/auth/user/ \
  -H "Authorization: Bearer your_jwt_token_here"
```

## Migration from Legacy System

If you're migrating from the previous authentication system:

1. **Update Frontend**: Change API endpoints from custom to dj-rest-auth endpoints
2. **Token Format**: The token format remains the same (JWT with custom claims)
3. **Error Handling**: Update error handling for dj-rest-auth response format
4. **Registration**: Use new registration endpoints with profile creation

## Troubleshooting

### Common Issues

1. **Social Login Fails**: Check provider credentials in environment variables
2. **Token Invalid**: Ensure JWT keys are properly configured
3. **CORS Errors**: Verify CORS settings include your frontend URL
4. **Profile Not Created**: Check that custom serializers are properly configured

### Debug Mode

Enable debug logging:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'api.views.auth': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'allauth': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## API Reference

### Complete dj-rest-auth Endpoints

All standard dj-rest-auth endpoints are available:

- Authentication: `/api/v1/auth/login/`, `/api/v1/auth/logout/`
- Registration: `/api/v1/auth/registration/`
- Password Management: `/api/v1/auth/password/reset/`, `/api/v1/auth/password/change/`
- User Management: `/api/v1/auth/user/`
- Social Authentication: `/api/v1/auth/{provider}/`

### Custom JWT Claims

JWT tokens include these custom claims:

```json
{
  "user": {...},
  "profile": {...},
  "permissions": {...},
  "roles": [...],
  "social_accounts": [...],
  "is_staff": boolean,
  "is_superuser": boolean
}
```

This integration provides a complete, secure, and scalable social authentication system that works seamlessly with your existing authentication infrastructure.
