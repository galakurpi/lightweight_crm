# Deployment Checklist - Lightweight CRM

## 🚂 Railway Backend Deployment

### Prerequisites
- [ ] Railway account created
- [ ] GitHub repository connected
- [ ] Supabase database set up
- [ ] OpenAI API key ready

### Railway Setup
1. [ ] Create new Railway project
2. [ ] Connect GitHub repository
3. [ ] Add environment variables:
   - [ ] `SECRET_KEY=your-secret-key-here`
   - [ ] `DEBUG=False`
   - [ ] `SUPABASE_URL=your-supabase-url`
   - [ ] `SUPABASE_KEY=your-supabase-key`
   - [ ] `OPENAI_API_KEY=your-openai-key`
   - [ ] `CORS_ALLOW_ALL_ORIGINS=True` (temporarily)
4. [ ] Add Redis service for Celery
5. [ ] Deploy and get Railway URL

## 🔺 Vercel Frontend Deployment

### Prerequisites
- [ ] Vercel account created
- [ ] Railway backend URL ready

### Vercel Setup
1. [ ] Import project from GitHub
2. [ ] Set framework preset: `Create React App`
3. [ ] Set root directory: `frontend`
4. [ ] Add environment variable:
   - [ ] `REACT_APP_API_URL=https://your-railway-url.railway.app`
5. [ ] Deploy and get Vercel URL

## 🔧 Final Configuration

### Update CORS Settings
1. [ ] Copy your Vercel domain (e.g., `https://your-app.vercel.app`)
2. [ ] Update Railway environment variables:
   - [ ] Set `CORS_ALLOW_ALL_ORIGINS=False`
3. [ ] Update `backend/settings.py` CORS_ALLOWED_ORIGINS to include your Vercel domain
4. [ ] Redeploy Railway backend

### Test Deployment
- [ ] Visit your Vercel frontend URL
- [ ] Test lead creation/editing
- [ ] Test AI chat functionality
- [ ] Test Kanban drag & drop

## 🎯 Important URLs to Save
- **Frontend (Vercel)**: https://your-app.vercel.app
- **Backend (Railway)**: https://your-backend.railway.app
- **Railway Dashboard**: https://railway.app/dashboard
- **Vercel Dashboard**: https://vercel.com/dashboard

## 🚨 Troubleshooting
- **CORS errors**: Check CORS_ALLOWED_ORIGINS includes your Vercel domain
- **API connection failed**: Verify REACT_APP_API_URL in Vercel
- **Chat not working**: Check OpenAI API key and Redis service in Railway
- **Database errors**: Verify Supabase credentials in Railway

## 📝 Post-Deployment Tasks
- [ ] Update DNS if using custom domain
- [ ] Set up monitoring/logging
- [ ] Configure CI/CD pipelines
- [ ] Update documentation with live URLs 