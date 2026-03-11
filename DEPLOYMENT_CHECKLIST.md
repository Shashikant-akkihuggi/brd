# Deployment Checklist - Railway/Render

## Pre-Deployment Verification

- [x] Removed invalid `python-cors` dependency
- [x] Verified all packages exist on PyPI
- [x] Added diagnostic output to Dockerfiles
- [x] Confirmed CORS uses FastAPI built-in middleware
- [x] Both requirements files validated

## Railway Deployment Steps

### 1. Clear Build Cache
```
Dashboard → Project → Settings → Clear Build Cache
```

### 2. Environment Variables
Set these in Railway dashboard:
```
DATABASE_URL=postgresql://postgres:password@host:5432/dbname
SECRET_KEY=your-secret-key-min-32-chars
GEMINI_API_KEY=your-gemini-api-key
CORS_ORIGINS=https://your-frontend.railway.app
DEBUG=false
```

### 3. Build Configuration
- **Root Directory**: `/` (leave empty)
- **Dockerfile Path**: `Dockerfile` (uses root Dockerfile)
- **Build Command**: (leave empty - uses Dockerfile)
- **Start Command**: (leave empty - uses Dockerfile CMD)

### 4. Deploy
```
Click "Deploy" or push to connected branch
```

### 5. Monitor Build Logs
Look for:
```
=== Contents of requirements.txt ===
fastapi==0.109.0
...
Successfully installed fastapi-0.109.0 ...
```

## Render Deployment Steps

### 1. Clear Build Cache
```
Dashboard → Service → Manual Deploy → Clear build cache & deploy
```

### 2. Environment Variables
Set these in Render dashboard:
```
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
GEMINI_API_KEY=your-api-key
CORS_ORIGINS=https://your-app.onrender.com
PYTHON_VERSION=3.11.0
```

### 3. Build Configuration
- **Environment**: Docker
- **Dockerfile Path**: `./Dockerfile`
- **Docker Context**: `.`

### 4. Deploy
```
Click "Manual Deploy" → "Deploy latest commit"
```

## Verification After Deployment

### 1. Check Health Endpoint
```bash
curl https://your-app.railway.app/
# or
curl https://your-app.onrender.com/
```

### 2. Check API Docs
```
https://your-app.railway.app/docs
```

### 3. Test CORS
```bash
curl -H "Origin: https://your-frontend.com" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS \
     https://your-app.railway.app/api/projects
```

Should return CORS headers.

## Troubleshooting

### Build Still Fails?

1. **Check diagnostic output in logs**
   - Look for "=== Contents of requirements.txt ==="
   - Verify it shows the correct packages

2. **Verify Dockerfile being used**
   - Root `Dockerfile` should be used
   - Not `backend/Dockerfile`

3. **Check for custom build commands**
   - Remove any custom pip install commands
   - Let Dockerfile handle everything

4. **Contact platform support**
   - Request complete cache clear
   - Verify no old configurations persist

### Runtime Errors?

1. **Database connection**
   - Verify DATABASE_URL format
   - Check database is provisioned

2. **Missing environment variables**
   - All required vars set
   - No typos in variable names

3. **CORS errors**
   - Update CORS_ORIGINS with actual frontend URL
   - Include protocol (https://)

## Success Indicators

✅ Build completes without errors
✅ Container starts successfully
✅ Health endpoint responds
✅ API docs accessible at /docs
✅ CORS headers present in responses
✅ Database migrations run successfully

## Quick Test Commands

```bash
# Test locally first
docker build -t brd-test .
docker run -p 8000:8000 -e SECRET_KEY=test brd-test

# Test endpoint
curl http://localhost:8000/

# Should return: {"message": "BRD Generation Platform API"}
```

---

**Last Updated**: 2026-03-11
**Status**: Ready for deployment
