# Cross-Subdomain Authentication Production Deployment Guide

## Overview
This guide covers the deployment of cross-subdomain authentication fixes for the EducationHub application where:
- Frontend: `educationhub.io` (Next.js)
- Backend: `authz.educationhub.io` (Django)

## Critical Configuration Changes Made

### 1. Frontend Configuration (Next.js)

#### Environment Variables (.env.production)
```bash
NEXT_PUBLIC_BACKEND_API_URL=https://authz.educationhub.io
NEXT_PUBLIC_FRONTEND_URL=https://educationhub.io
NODE_ENV=production
```

#### Authentication Route Fixes
- **File**: `src/app/api/auth/login/route.ts`
- **Changes**: 
  - Cross-subdomain cookie support with domain=".educationhub.io"
  - SameSite policy changed from "strict" to "lax"
  - Environment-aware configuration

#### Proxy Route Enhancements
- **File**: `src/app/api/proxy/[...path]/route.ts`
- **Changes**: 
  - Enhanced cookie forwarding for cross-subdomain requests
  - Comprehensive debugging and logging
  - Environment detection logic

#### Debug Endpoint
- **File**: `src/app/api/debug-cookies/route.ts`
- **Purpose**: Diagnostic tool for troubleshooting authentication issues
- **Usage**: Access `/api/debug-cookies` to see environment and cookie status

### 2. Backend Configuration (Django)

#### Development Settings (settings.py)
- **CSRF_TRUSTED_ORIGINS**: Added production domains
- **CORS Configuration**: Enhanced for cross-subdomain support
- **JWT Settings**: Configured for HttpOnly cookies with SameSite="Lax"

#### Production Settings (production.py)
- **CSRF_TRUSTED_ORIGINS**: 
  ```python
  CSRF_TRUSTED_ORIGINS = [
      "https://educationhub.io",
      "https://authz.educationhub.io",
  ]
  ```
- **CORS_ALLOWED_ORIGINS**: Updated with production domains
- **JWT Auth Settings**: Secure production configuration
- **ALLOWED_REDIRECT_HOSTS**: Cross-subdomain redirect support

#### Environment Variables (.env.production)
Critical variables that must be configured in production:
- `SECRET_KEY`: Django secret key
- `PRIVATE_KEY_B64`: Base64-encoded JWT private key
- `PUBLIC_KEY_B64`: Base64-encoded JWT public key
- `WEB_CLIENT_URL`: https://educationhub.io
- `BACKEND_URL`: https://authz.educationhub.io
- `FRONTEND_URL`: https://educationhub.io

## Deployment Steps

### Step 1: Backend Deployment
1. **Deploy Django backend to `authz.educationhub.io`**
2. **Configure environment variables**:
   ```bash
   # Copy .env.production to production server
   # Update with actual production credentials
   SECRET_KEY=your-actual-secret-key
   PRIVATE_KEY_B64=your-actual-private-key
   PUBLIC_KEY_B64=your-actual-public-key
   # ... other variables
   ```
3. **Use production settings**:
   ```bash
   export DJANGO_SETTINGS_MODULE=main.production
   python manage.py migrate
   python manage.py collectstatic
   ```

### Step 2: Frontend Deployment
1. **Build frontend with production environment**:
   ```bash
   npm run build
   ```
2. **Deploy to `educationhub.io`**
3. **Ensure environment variables are set in production hosting**

### Step 3: DNS and SSL Configuration
1. **Ensure both domains have valid SSL certificates**
2. **Verify DNS records point to correct servers**
3. **Test HTTPS connectivity for both domains**

## Testing and Verification

### 1. Debug Endpoint Testing
Access the debug endpoint to verify configuration:
```
GET https://educationhub.io/api/debug-cookies
```

Expected response should show:
- Correct environment variables
- Cross-subdomain detection: true
- Backend URL pointing to authz.educationhub.io

### 2. Authentication Flow Testing
1. **Login Test**:
   ```
   POST https://educationhub.io/api/auth/login
   {
     "email": "test@example.com",
     "password": "password"
   }
   ```

2. **Auth Status Test**:
   ```
   GET https://educationhub.io/api/auth/auth-status
   ```

3. **Cookie Verification**:
   - Check browser dev tools for cookies
   - Verify domain is set to ".educationhub.io"
   - Confirm SameSite is "Lax"

### 3. Cross-Subdomain Request Testing
Test that authenticated requests from frontend reach backend:
```
GET https://educationhub.io/api/proxy/api/user/profile/
```

## Troubleshooting Guide

### Common Issues and Solutions

#### 1. 401 Authentication Errors
- **Cause**: CSRF_TRUSTED_ORIGINS not configured
- **Solution**: Verify production.py includes both domains in CSRF_TRUSTED_ORIGINS

#### 2. Cookies Not Set
- **Cause**: SameSite="strict" blocking cross-subdomain
- **Solution**: Confirm SameSite="Lax" in both frontend and backend

#### 3. Environment Detection Issues
- **Cause**: Missing or incorrect environment variables
- **Solution**: Use debug endpoint to verify environment configuration

#### 4. CORS Errors
- **Cause**: Backend not configured for frontend domain
- **Solution**: Verify CORS_ALLOWED_ORIGINS includes educationhub.io

## Security Considerations

### Production Security Settings
- **HTTPS Only**: All cookies marked as Secure in production
- **HttpOnly Cookies**: JWT tokens not accessible via JavaScript
- **SameSite Lax**: Balanced security for cross-subdomain functionality
- **CSRF Protection**: Enabled with trusted origins configuration

### Environment Variable Security
- Never commit `.env.production` to version control
- Use secure environment variable management in production
- Rotate JWT keys regularly
- Use strong, unique SECRET_KEY

## Monitoring and Maintenance

### Log Monitoring
Monitor these log patterns for authentication issues:
- Django: CSRF verification failed
- Frontend: Cookie forwarding errors
- Backend: JWT validation failures

### Health Checks
Regular checks to perform:
1. Authentication flow end-to-end
2. Cookie domain and security settings
3. CSRF token validation
4. Cross-subdomain request success

## Additional Notes

### JWT Key Generation
To generate new JWT keys for production:
```bash
# Generate private key
openssl genrsa -out private_key.pem 2048

# Generate public key
openssl rsa -in private_key.pem -pubout -out public_key.pem

# Base64 encode for environment variables
base64 -i private_key.pem
base64 -i public_key.pem
```

### Environment Variable Template
Use the `.env.production` template as a starting point and update all placeholder values with actual production credentials.

---

## Summary of Files Modified

### Frontend (Next.js)
- `.env.production` - Production environment variables
- `src/app/api/auth/login/route.ts` - Cross-subdomain cookie handling
- `src/app/api/proxy/[...path]/route.ts` - Enhanced proxy with debugging
- `src/app/api/debug-cookies/route.ts` - New diagnostic endpoint

### Backend (Django)
- `main/settings.py` - Development configuration with cross-subdomain support
- `main/production.py` - Production configuration with security settings
- `.env.production` - Production environment variable template

This deployment addresses the root cause of 401 authentication errors by properly configuring cross-subdomain authentication between educationhub.io and authz.educationhub.io.
