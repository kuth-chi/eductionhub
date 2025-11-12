# Social Login URL Length Fix

## Problem
Social login callback was failing with error:
```
django.core.exceptions.DisallowedRedirect: Unsafe redirect exceeding 2048 characters
```

## Root Cause
The backend was encoding all authentication data (tokens, user info, profile, permissions, roles, and social accounts with `extra_data`) as a base64 string in the URL query parameter. The `extra_data` field from social accounts (especially from providers like Google or Facebook) can contain large amounts of data, causing the redirect URL to exceed Django's 2048 character limit.

## Solution
Changed the social login callback flow to use a simpler, more secure approach:

### Backend Changes (`api/views/social_callback.py`)
1. **Removed heavy data encoding**: No longer pass user data, tokens, or social account info in URL
2. **Simplified redirect**: Now only passes `status=success` parameter
3. **Cookies still set**: JWT tokens are still set as HttpOnly cookies via `set_auth_cookies()`
4. **Frontend fetches data**: Frontend now calls `/api/v1/auth-status/` to get user data after successful redirect

**Before:**
```python
# Encoded all this data in URL (could exceed 2048 chars)
auth_data = {
    "status": "ok",
    "refresh": str(refresh),
    "access": str(access_token),
    "user": {...},
    "profile": {...},
    "permissions": [...],
    "roles": [...],
    "social_accounts": [{...extra_data...}],  # This could be huge!
}
auth_data_encoded = base64.b64encode(json.dumps(auth_data).encode()).decode()
redirect_url = f"{frontend_url}?auth_data={auth_data_encoded}"
```

**After:**
```python
# Minimal redirect parameter
redirect_url = f"{frontend_url}?status=success"
# Tokens still set via HttpOnly cookies
response = redirect(redirect_url)
response = set_auth_cookies(response, str(access_token), str(refresh))
```

### Frontend Changes (`src/app/auth/callback/page.tsx`)
1. **Check for `status=success`**: Primary flow now checks for this simple parameter
2. **Call auth-status endpoint**: Uses `checkAuthStatus()` to fetch user data from backend
3. **Legacy support maintained**: Still handles old `auth_data` parameter for backward compatibility

**Flow:**
```
1. User clicks social login → redirected to provider
2. Provider redirects back to backend callback
3. Backend sets JWT cookies + redirects to frontend with ?status=success
4. Frontend detects success, calls checkAuthStatus()
5. Backend returns full user data via /api/v1/auth-status/ (reading cookies)
6. User is logged in and redirected to profile
```

## Benefits
1. **No URL length issues**: Minimal redirect parameter (just `status=success`)
2. **More secure**: Sensitive data not exposed in URL (URLs are logged, cached, etc.)
3. **Cleaner separation**: Backend handles auth, frontend fetches user data via proper API
4. **Better error handling**: Simpler flow with fewer points of failure
5. **Cookie-based auth**: Leverages existing HttpOnly cookie infrastructure

## Testing
1. Test social login with Google (large extra_data)
2. Test social login with GitHub
3. Test social login with Facebook
4. Verify cookies are set correctly
5. Verify auth-status endpoint returns correct data
6. Test redirect to intended page after login

## Related Files
- Backend: `api/views/social_callback.py`
- Frontend: `src/app/auth/callback/page.tsx`
- Auth hook: `src/hooks/use-auth.ts` (checkAuthStatus method)
- Auth status endpoint: `api/views/auth/auth_viewset.py`

## Date
November 12, 2025
