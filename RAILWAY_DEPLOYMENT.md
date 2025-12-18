# Railway Deployment Guide

## ✅ Changes Made for Railway Deployment

All necessary changes have been made to serve the frontend from your API container on Railway!

### Files Modified:

1. **`frontend/script.js`** (Line 2-3)
   - Changed from: `const API_BASE_URL = 'https://library-production-9ee7.up.railway.app';`
   - Changed to: `const API_BASE_URL = window.location.origin;`
   - This automatically uses the same domain for API calls

2. **`src/predict_api.py`** 
   - Added imports for `StaticFiles` and `FileResponse`
   - Added frontend static file mounting at `/static`
   - Changed root route `/` to serve `index.html` instead of JSON
   - `/health` endpoint moved to dedicated route

3. **`Dockerfile`**
   - Added line to copy frontend files: `COPY frontend/ ./frontend/`

4. **`frontend/index.html`**
   - Updated script path from `script.js` to `/static/script.js`

## 🚀 Deploy to Railway

### Option 1: Push to GitHub (Automatic Deploy)

```powershell
# Add all changes
git add .

# Commit changes
git commit -m "Configure frontend to be served from API container"

# Push to GitHub
git push origin main
```

Railway will automatically detect the push and redeploy!

### Option 2: Railway CLI

```powershell
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link project
railway link

# Deploy
railway up
```

## 🎯 After Deployment

### Access Your Application:

- **Frontend Dashboard**: `https://your-project.up.railway.app/`
- **API Health**: `https://your-project.up.railway.app/health`
- **API Docs**: `https://your-project.up.railway.app/docs`
- **Make Prediction**: `https://your-project.up.railway.app/predict`

### Verify Deployment:

1. Visit your Railway URL - you should see the **dashboard** (not JSON)
2. Check "Model Status" badge - should show "Model Active"
3. Fill out the prediction form and test
4. Check browser console for any errors (F12)

## 🔧 Railway Configuration

### Port Configuration:
- **Port**: `8000` (already configured in your Dockerfile)
- Railway auto-detects this from `EXPOSE 8000`

### Environment Variables (Optional):
Add in Railway dashboard if needed:
- `MODEL_PATH=/app/models/final_churn_prediction_pipeline.pkl`
- `PYTHONUNBUFFERED=1`

## 🐛 Troubleshooting

### If you still see JSON instead of the dashboard:

1. **Clear browser cache** (Ctrl+Shift+Delete)
2. **Check Railway logs**:
   ```
   railway logs
   ```
3. **Verify frontend files were copied**:
   - Check deployment logs for "Frontend static files mounted at /static"

### If CSS/JS not loading:

1. Open browser console (F12)
2. Check for 404 errors on `/static/script.js`
3. Verify file paths in Railway deployment

### If API calls fail:

1. Check browser console (F12) → Network tab
2. Verify API calls go to same domain (no CORS errors)
3. Test `/health` endpoint directly

## 📦 What's Included in This Deployment

✅ FastAPI backend (port 8000)  
✅ ML model serving  
✅ Frontend dashboard (served from root `/`)  
✅ API documentation (`/docs`)  
✅ Health monitoring (`/health`)  
✅ Metrics endpoint (`/metrics`)  

## 🎉 Next Steps

1. **Push to GitHub**: `git push origin main`
2. **Wait for Railway deployment** (~2-3 minutes)
3. **Visit your Railway URL**
4. **Test predictions** with the dashboard
5. **Share your app** with the team!

---

**Your Railway URL**: Check Railway dashboard for your deployment URL

**Questions?** Check Railway logs or deployment status in the dashboard.
