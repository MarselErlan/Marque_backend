# 🚀 Fix Railway Deployment - 403 Forbidden

**Error:** `Failed to upload code with status code 403 Forbidden`

---

## 🔧 Quick Fixes

### Option 1: Use Git Push (Recommended)

Railway works best with Git deployment:

```bash
# 1. Make sure all changes are committed
git add .
git commit -m "feat: Enhanced authentication flow with user state management"

# 2. Push to GitHub
git push origin main

# Railway will auto-deploy from GitHub!
```

**Why this works:**

- Railway is connected to your GitHub repo
- Automatic deployments on push
- No CLI needed

---

### Option 2: Re-authenticate Railway CLI

```bash
# 1. Logout from Railway
railway logout

# 2. Login again
railway login

# 3. Link to your project
railway link

# 4. Try deploy again
railway up
```

---

### Option 3: Deploy via Railway Dashboard

1. Go to https://railway.app
2. Find your `marque` project
3. Click **Settings** → **Deployments**
4. Click **Deploy Now**
5. Railway will pull from GitHub and deploy

---

## ✅ Recommended: Git Push Method

This is the easiest and most reliable:

```bash
# Check current git status
git status

# Stage all changes
git add .

# Commit with message
git commit -m "feat: Complete authentication flow with database state management

- Users auto-saved on verification
- is_active=true on login
- is_active=false on logout
- No duplicate users
- New token on each login
- Enhanced profile APIs ready"

# Push to GitHub (Railway will auto-deploy)
git push origin main
```

---

## 🔍 Check Railway Connection

```bash
# See which project you're linked to
railway status

# If not linked:
railway link
# Select your project from the list

# Try again
railway up
```

---

## 📊 Verify Deployment

After pushing to GitHub:

1. **Check Railway Dashboard:**

   - Go to https://railway.app/dashboard
   - Find your project
   - Watch the deployment logs
   - Wait for "Deployment successful"

2. **Test the API:**

```bash
# Health check
curl https://marquebackend-production.up.railway.app/health

# Test auth
curl -X POST https://marquebackend-production.up.railway.app/api/v1/auth/send-verification \
  -H "Content-Type: application/json" \
  -d '{"phone": "+13128059851"}'
```

---

## 🎯 What Gets Deployed

When you push, Railway will deploy:

✅ **Authentication Changes:**

- ✅ Enhanced login flow (no duplicate users)
- ✅ Proper logout (sets is_active=false)
- ✅ Login again (reactivates user)

✅ **Profile APIs:**

- ✅ 16 new profile endpoints
- ✅ Addresses management
- ✅ Payment methods
- ✅ Orders history
- ✅ Notifications

✅ **Database Updates:**

- ✅ User state management
- ✅ is_active tracking
- ✅ is_verified tracking
- ✅ last_login timestamps

---

## ⚠️ Troubleshooting

### Error: "Not linked to a project"

```bash
railway link
# Select your project
```

### Error: "No git remote"

```bash
git remote -v
# If no origin, add it:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
```

### Error: "Permission denied"

```bash
# Re-authenticate
railway logout
railway login
```

---

## 🚀 Deploy Now!

**Fastest method:**

```bash
git add .
git commit -m "feat: Authentication and profile APIs complete"
git push origin main
```

Then watch deployment at: https://railway.app/dashboard

**Deployment usually takes 2-3 minutes.**

---

## ✅ After Deployment

Test your new features:

```bash
# 1. Test authentication
curl https://marquebackend-production.up.railway.app/api/v1/auth/markets

# 2. Test profile endpoints (need token)
# Get token first via Postman, then:
curl https://marquebackend-production.up.railway.app/api/v1/profile/addresses \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📝 Deployment Checklist

- [ ] All changes committed (`git status` shows clean)
- [ ] Pushed to GitHub (`git push origin main`)
- [ ] Railway deployment started (check dashboard)
- [ ] Deployment successful (green checkmark)
- [ ] API health check passes
- [ ] Test authentication flow
- [ ] Test profile APIs

---

**Ready to deploy?** Just run:

```bash
git add .
git commit -m "feat: Enhanced auth flow and profile APIs"
git push origin main
```

Railway will handle the rest! 🚀
