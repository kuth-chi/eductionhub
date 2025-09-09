# Seamless Authentication Setup

This document describes the seamless authentication system between Django backend (with AllAuth SocialAccount) and Next.js frontend using JWT tokens.

## Overview

The authentication system provides:
- **Regular Login**: Username/password authentication with JWT tokens
- **Social Login**: Google, Facebook, and Telegram authentication via AllAuth
- **Seamless Integration**: Both authentication methods work together seamlessly
- **Session Sync**: Django sessions and JWT tokens are synchronized
- **Automatic Token Refresh**: Tokens are automatically refreshed when needed

## Backend Setup (Django)

### 1. Authentication Views

The backend provides several authentication endpoints:

- `POST /api/v1/token/` - Regular login with username/password
- `POST /api/v1/social-jwt/` - Get JWT tokens for social login users
- `GET /api/v1/auth-status/` - Check authentication status
- `POST /api/v1/logout/` - Logout and clear tokens
- `GET /auth/social/callback/` - Social login callback
- `GET /auth/social/status/` - Check social login status

### 2. Middleware

Two custom middleware classes handle authentication:

- **JWTSessionMiddleware**: Syncs JWT tokens with Django sessions
- **SocialAuthMiddleware**: Handles social authentication redirects

### 3. JWT Configuration

JWT tokens include:
- User ID for middleware authentication
- User profile information
- Permissions and roles
- Social account information
- User agent and IP for security

## Frontend Setup (Next.js)

### 1. Authentication Hook

The `useAuth` hook provides:
- Login/logout functionality
- Token management
- Automatic token refresh
- Social login integration
- Authentication status checking

### 2. Social Login Component

The `SocialLogin` component provides:
- Google, Facebook, and Telegram login buttons
- Loading states
- Error handling
- Redirect to Django social login

### 3. Auth Fetch Utility

The `authFetch` utility provides:
- Automatic token inclusion in requests
- Automatic token refresh on 401 errors
- Cookie-based authentication support
- Error handling

## Authentication Flow

### Regular Login Flow

1. User enters username/password
2. Frontend calls `POST /api/v1/token/`
3. Backend validates credentials and returns JWT tokens
4. Frontend stores tokens in localStorage
5. Tokens are automatically included in subsequent requests

### Social Login Flow

1. User clicks social login button
2. Frontend redirects to Django social login URL
3. Django handles OAuth flow with provider
4. Django redirects to callback with auth data
5. Frontend processes auth data and stores tokens
6. User is redirected to dashboard

### Token Refresh Flow

1. Frontend detects expired token
2. Frontend calls `POST /api/token/refresh/` with refresh token
3. Backend validates refresh token and returns new access token
4. Frontend updates stored tokens
5. Request continues with new token

## Environment Variables

### Backend (Django)

```bash
# JWT Settings
PRIVATE_KEY_B64=your_base64_encoded_private_key
PUBLIC_KEY_B64=your_base64_encoded_public_key
SECRET_KEY=your_django_secret_key

# Social Auth Settings
GOOGLE_AUTH_CLIENT_ID=your_google_client_id
GOOGLE_AUTH_SECRET=your_google_client_secret
TELEGRAM_BOT_ID=your_telegram_bot_id
TELEGRAM_LOGIN_PUBLIC_KEY=your_telegram_public_key

# Frontend URL
FRONTEND_URL_ORIGIN=http://localhost:3000
```

### Frontend (Next.js)

```bash
NEXT_PUBLIC_BACKEND_API_URL=http://localhost:8000
```

## Usage Examples

### Regular Login

```typescript
import { useAuth } from '@/hooks/use-auth';

function LoginComponent() {
  const { login } = useAuth();
  
  const handleLogin = async (username: string, password: string) => {
    try {
      await login(username, password);
      // Redirect to dashboard
    } catch (error) {
      // Handle error
    }
  };
}
```

### Social Login

```typescript
import { SocialLogin } from '@/components/social-login';

function LoginPage() {
  return (
    <div>
      <form>
        {/* Regular login form */}
      </form>
      <SocialLogin onError={(error) => console.error(error)} />
    </div>
  );
}
```

### Protected API Calls

```typescript
import { authFetch } from '@/lib/auth-fetch';

async function fetchUserData() {
  const response = await authFetch('/api/v1/profiles/my-profile/');
  return response.json();
}
```

### Check Authentication Status

```typescript
import { useAuth } from '@/hooks/use-auth';

function App() {
  const { isAuthenticated, isLoading } = useAuth();
  
  if (isLoading) return <LoadingSpinner />;
  
  return isAuthenticated ? <Dashboard /> : <LoginPage />;
}
```

## Security Features

1. **Token Expiration**: Access tokens expire after 1 hour
2. **Refresh Tokens**: Valid for 7 days
3. **User Agent Binding**: Tokens are bound to user agent
4. **IP Binding**: Tokens are bound to IP address (first two octets)
5. **HTTPS Only**: Cookies are secure in production
6. **HttpOnly Cookies**: Tokens stored in HttpOnly cookies
7. **CSRF Protection**: Django CSRF protection enabled

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure CORS settings are correct in Django
2. **Token Expired**: Check if tokens are being refreshed properly
3. **Social Login Not Working**: Verify OAuth provider settings
4. **Session Issues**: Check middleware order in Django settings

### Debug Steps

1. Check browser network tab for failed requests
2. Check Django logs for authentication errors
3. Verify environment variables are set correctly
4. Test social login providers individually
5. Check token expiration times

## Production Considerations

1. **HTTPS**: Enable HTTPS in production
2. **Secure Cookies**: Set `secure=True` for cookies
3. **Domain Settings**: Configure proper domains for cookies
4. **Rate Limiting**: Implement rate limiting for auth endpoints
5. **Logging**: Add comprehensive logging for auth events
6. **Monitoring**: Monitor authentication success/failure rates

## Migration from Previous Setup

If migrating from a different authentication system:

1. Update frontend to use new auth hook
2. Replace old API calls with `authFetch`
3. Update protected routes to use new auth context
4. Test both regular and social login flows
5. Update environment variables
6. Test token refresh functionality

## API Reference

### Authentication Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/token/` | POST | Regular login |
| `/api/v1/social-jwt/` | POST | Get JWT for social user |
| `/api/v1/auth-status/` | GET | Check auth status |
| `/api/v1/logout/` | POST | Logout |
| `/auth/social/callback/` | GET | Social login callback |
| `/auth/social/status/` | GET | Social login status |

### JWT Token Structure

```json
{
  "user_id": 123,
  "profile": {
    "id": "uuid",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "photo": "url"
  },
  "permissions": ["app.view_profile"],
  "roles": ["user"],
  "social_accounts": [
    {
      "provider": "google",
      "uid": "123456789",
      "extra_data": {}
    }
  ],
  "ua": "Mozilla/5.0...",
  "ip": "192.168",
  "exp": 1234567890
}
``` 