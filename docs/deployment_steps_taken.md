# Deployment Steps Taken - Lightweight CRM

## Chronological List of Errors and Fixes

### 1. Railway Detected Node.js Instead of Django
**Error**: Railway build failed with `"cd backend && pip install..." did not complete successfully: exit code: 127`
**Cause**: Root level `package.json` and `server.js` files confused Railway's auto-detection
**Fix**: 
- Deleted root `package.json` and `server.js` files
- Created `.railwayignore` to exclude frontend
- Added proper `Procfile`, `runtime.txt`, and `build.sh`
**Result**: Railway correctly detected Python/Django project

### 2. Missing Production Configuration Files
**Error**: Railway couldn't determine how to run the Django app
**Cause**: No deployment configuration files
**Fix**: Created deployment files:
- `Procfile`: `web: cd backend && python manage.py migrate && gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT`
- `runtime.txt`: `python-3.9.18`
- `requirements.txt`: Added `gunicorn==21.2.0`

### 3. Django Static Files Not Configured
**Error**: Static files would not be served in production
**Cause**: Missing `STATIC_ROOT` setting
**Fix**: Added to `backend/settings.py`:
```python
STATIC_ROOT = BASE_DIR / 'staticfiles'
DEBUG = False
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,*.railway.app').split(',')
```

### 4. Frontend Environment Variable Missing
**Error**: Frontend making API calls to `localhost:8000` instead of Railway backend
**Cause**: `REACT_APP_API_URL` not set in Vercel
**Fix**: Added environment variable in Vercel dashboard:
- `REACT_APP_API_URL=https://lightweightcrm-production.up.railway.app`

### 5. CORS Policy Blocking Frontend-Backend Connection
**Error**: `Access-Control-Allow-Origin header is present on the requested resource`
**Cause**: Django backend not configured to allow requests from Vercel domain
**Fix**: Added Vercel domains to `backend/settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://lightweight-d6519wrjz-jons-projects-f84a4607.vercel.app",
    "https://lightweight-crm-indol.vercel.app",
]
```

### 6. 401 Unauthorized Errors on All API Calls
**Error**: `Failed to load resource: the server responded with a status of 401` on `/auth/user/`, `/leads/`, etc.
**Cause**: Session cookies not configured for cross-origin requests (Vercel → Railway)
**Fix**: Added production session and CSRF settings to `backend/settings.py`:
```python
# Session cookies for cross-origin (Vercel → Railway)
SESSION_COOKIE_SECURE = True  # HTTPS only
SESSION_COOKIE_SAMESITE = 'None'  # Allow cross-origin
SESSION_COOKIE_HTTPONLY = True  # Security

# CSRF settings
CSRF_TRUSTED_ORIGINS = [
    "https://lightweight-d6519wrjz-jons-projects-f84a4607.vercel.app",
    "https://lightweight-crm-indol.vercel.app",
]
CSRF_COOKIE_SAMESITE = 'None'
```
**Git Commit**: `4bce76c` - "Fix 401 auth errors: Configure session cookies and CSRF for cross-origin requests"

### 7. Session Cookies Still Not Working in Production
**Error**: 401 errors persisting after login - session cookies not being maintained
**Cause**: Session cookie settings needed explicit configuration for cross-origin HTTPS
**Fix**: Updated session configuration to be explicit about cross-origin behavior:
```python
SESSION_COOKIE_SECURE = True  # Always HTTPS
SESSION_COOKIE_SAMESITE = 'None'  # Required for cross-origin
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_NAME = 'crm_sessionid'
```
Added debugging logs to track session creation and authentication
**Git Commit**: `070ca19` - "Resolve merge conflict: Keep debugging logs, remove auth bypass"

### 8. Dynamic Vercel URLs Breaking CORS (Chicken-Egg Problem)
**Error**: `No 'Access-Control-Allow-Origin' header` every time Vercel creates new deployment with different hash
**Cause**: Each Vercel deployment gets a new random URL like `lightweight-abc123.vercel.app`, breaking CORS
**Fix**: Replaced specific URLs with flexible regex pattern:
```python
# Allow any Vercel deployment for this project
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://lightweight-.*\.vercel\.app$",
]

# CSRF wildcard for Vercel domains
CSRF_TRUSTED_ORIGINS = [
    "https://lightweight-crm-indol.vercel.app",
    "https://*.vercel.app",
]
```
**Git Commit**: `c23f8d0` - "Fix dynamic Vercel URLs: Use regex pattern to allow all lightweight-*.vercel.app domains"
**Result**: ✅ CORS now works for any future Vercel deployment automatically

### 9. New Vercel Deployment URL Breaking CORS Again
**Error**: `No 'Access-Control-Allow-Origin' header` on new Vercel URL `https://lightweight-qgudsb820-jons-projects-f84a4607.vercel.app`
**Cause**: Railway hadn't redeployed with latest CORS regex pattern from previous fix
**Fix**: Triggered Railway redeploy by pushing small comment change to `backend/settings.py`
**Git Commit**: `40ee837` - "Trigger Railway redeploy: Update CORS regex comment for new Vercel URL"
**Result**: 🔄 Railway redeploying with regex pattern that should match all lightweight-*.vercel.app URLs

### 10. Django Backend Startup Failure After CORS Fix
**Error**: `python: can't open file '/app/backend/manage.py': [Errno 2] No such file or directory`
**Cause**: Procfile was trying to run `cd backend && python manage.py` but `manage.py` is in root directory
**Fix**: Updated Procfile to correct path:
```
web: python manage.py migrate && gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT
```
**Result**: ✅ Railway backend started successfully, CORS issues resolved

### 11. Chat Status Polling 401 Unauthorized Errors
**Error**: `GET /chat/status/{task_id}/ 401 (Unauthorized)` during chat message polling
**Cause**: Chat status polling requests missing `credentials: 'include'` header for session cookies
**Fix**: Added credentials to polling fetch in `frontend/src/components/ChatWidget.js`:
```javascript
const response = await fetch(`${API_BASE_URL}/chat/status/${taskId}/`, {
  credentials: 'include', // Include session cookies for authentication
});
```
**Result**: ✅ Chat status polling now includes session cookies, no more 401 errors

### 12. Manifest.json 401 Errors on Vercel
**Error**: `Failed to load resource: the server responded with a status of 401 ()` for `/manifest.json`
**Cause**: Vercel routing configuration causing static files to get authentication headers
**Fix**: Added explicit routes for static files in `vercel.json`:
```json
"routes": [
  {
    "src": "/manifest.json",
    "dest": "/frontend/manifest.json",
    "headers": {
      "Cache-Control": "public, max-age=86400"
    }
  },
  {
    "src": "/favicon.ico",
    "dest": "/frontend/favicon.ico"
  },
  {
    "src": "/logo(.*).png",
    "dest": "/frontend/logo$1.png"
  }
]
```
**Result**: ✅ Static files served properly without authentication headers

### 13. Celery Workers Being Killed by Railway Memory Limits
**Error**: `Worker (pid:X) was sent SIGKILL! Perhaps out of memory?` - Chat tasks stuck in PENDING state forever
**Cause**: Railway containers have limited memory, running both Django and Celery workers exceeded limits
**Fix**: Implemented threading fallback approach:
1. Skip Celery entirely to avoid memory issues
2. Use Python threading for background chat processing
3. Store results in Django cache instead of Redis/Celery backend
4. Updated chat status endpoint to check cache first

```python
# Force threading fallback since Celery workers keep getting killed
print(f"🔄 Skipping Celery (workers killed by Railway) - using threading...")

# Threading approach when Celery workers are killed by memory limits
import threading
import uuid
from django.core.cache import cache

# Generate a task ID for polling
task_id = str(uuid.uuid4())

# Set initial status
cache.set(f"task_{task_id}", {'state': 'PROCESSING', 'status': 'Processing your message...'}, 300)

def process_in_thread():
    # Process chat message in background thread
    # Store results in cache when complete

thread = threading.Thread(target=process_in_thread)
thread.daemon = True
thread.start()
```

Updated Procfile for better memory usage:
```
web: python manage.py migrate && gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --threads 2
```
**Result**: ✅ Chat processing works reliably without memory issues, no more infinite polling

## Admin Login Credentials
- **Email**: `admin@crm.local`
- **Password**: `admin123`

## Final Working Configuration

### Railway Backend
- **URL**: `https://lightweightcrm-production.up.railway.app`
- **Status**: ✅ Working
- **Test Endpoint**: `/test/` returns `{"message":"Django API is working!","status":"success"}`
- **Chat Processing**: Threading-based (Celery disabled due to memory constraints)

### Vercel Frontend  
- **URL**: `https://lightweight-d6519wrjz-jons-projects-f84a4607.vercel.app`
- **Status**: ✅ Connected to backend
- **Environment Variable**: `REACT_APP_API_URL` pointing to Railway
- **Static Files**: Properly routed and cached

## Required Environment Variables

### Railway (from .env)
```
SECRET_KEY=your-secret-key
DEBUG=False
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
OPENAI_API_KEY=your-openai-key
CORS_ALLOW_ALL_ORIGINS=False
```

### Vercel
```
REACT_APP_API_URL=https://lightweightcrm-production.up.railway.app
```

## Key Lessons Learned

1. **CORS with Credentials**: When using `credentials: 'include'`, cannot use wildcard `*` for CORS origins
2. **Railway Memory Limits**: Free tier has strict memory limits that kill Celery workers - threading is more reliable
3. **Vercel Dynamic URLs**: Use regex patterns for CORS to handle dynamic preview deployment URLs
4. **Session Cookies Cross-Origin**: Requires `SameSite=None` and `Secure=True` for HTTPS
5. **Static File Routing**: Explicit Vercel routes prevent authentication headers on static assets
6. **Railway File Paths**: Always verify file locations match Procfile commands
