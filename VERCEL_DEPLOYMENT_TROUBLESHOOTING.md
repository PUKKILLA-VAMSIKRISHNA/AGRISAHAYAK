# Vercel Deployment Troubleshooting Guide

## 🚨 **Issue: Project Not Showing in Vercel Deployments**

If your project isn't appearing in the Vercel deployments section after pushing to Git, follow these steps:

### 1. **Check Vercel Project Configuration**

#### Step 1: Verify Repository Connection
1. Go to [vercel.com](https://vercel.com)
2. Sign in to your account
3. Go to **Dashboard**
4. Check if your project `agrisahayak` is listed
5. If not, you need to reconnect the repository

#### Step 2: Reconnect Repository (if needed)
1. Click **"New Project"**
2. Import your GitHub repository: `PUKKILLA-VAMSIKRISHNA/AGRISAHAYAK`
3. Configure the project settings:
   - **Framework Preset**: Other
   - **Root Directory**: `./` (leave empty)
   - **Build Command**: Leave empty (not needed for Python)
   - **Output Directory**: Leave empty
   - **Install Command**: Leave empty

### 2. **Check Git Repository Status**

Your repository details:
- **Repository**: `https://github.com/PUKKILLA-VAMSIKRISHNA/AGRISAHAYAK.git`
- **Branch**: `main`
- **Latest Commit**: `26ce46a` - "Add test script and trigger deployment"

### 3. **Manual Deployment Trigger**

#### Option A: Using Vercel CLI
```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy from current directory
vercel --prod
```

#### Option B: Using Vercel Dashboard
1. Go to your project in Vercel Dashboard
2. Click **"Deployments"** tab
3. Click **"Redeploy"** on the latest deployment
4. Or click **"Deploy"** to trigger a new deployment

### 4. **Check Environment Variables**

Ensure these are set in Vercel Dashboard:
1. Go to **Settings** > **Environment Variables**
2. Verify these variables are set:
   - `DATABASE_URL`
   - `SECRET_KEY`
   - `GEMINI_API_KEY`
   - `BASE_URL`

### 5. **Verify Vercel Configuration**

Your `vercel.json` should look like this:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "main.py",
      "use": "@vercel/python",
      "config": { 
        "maxLambdaSize": "50mb",
        "runtime": "python3.9"
      }
    }
  ],
  "routes": [
    { "src": "/static/(.*)", "dest": "/main.py" },
    { "src": "/favicon.ico", "dest": "/main.py" },
    { "src": "/favicon.png", "dest": "/main.py" },
    { "src": "/(.*)", "dest": "/main.py" }
  ],
  "env": {
    "PYTHONPATH": ".",
    "FLASK_ENV": "production"
  },
  "functions": {
    "main.py": {
      "maxDuration": 30
    }
  }
}
```

### 6. **Check GitHub Repository**

1. Go to [GitHub Repository](https://github.com/PUKKILLA-VAMSIKRISHNA/AGRISAHAYAK)
2. Verify the latest commits are there
3. Check if the repository is public (Vercel needs access)

### 7. **Force Redeploy**

If the project exists but isn't updating:

#### Method 1: Empty Commit
```bash
git commit --allow-empty -m "Force redeploy"
git push origin main
```

#### Method 2: Update Vercel Configuration
```bash
# Add a comment to vercel.json
echo "// Updated: $(date)" >> vercel.json
git add vercel.json
git commit -m "Update Vercel config"
git push origin main
```

### 8. **Check Vercel Logs**

1. Go to Vercel Dashboard
2. Click on your project
3. Go to **Functions** tab
4. Check for any error logs
5. Look for deployment failures

### 9. **Alternative: Create New Project**

If nothing works:
1. Delete the existing project in Vercel
2. Create a new project
3. Import the same repository
4. Set up environment variables again
5. Deploy

### 10. **Test Deployment Status**

Run this command to check if deployment is working:
```bash
python -c "import requests; r = requests.get('https://agrisahayak.vercel.app/health'); print('Status:', r.status_code); print(r.json())"
```

## 🔧 **Quick Fix Commands**

```bash
# Check Git status
git status
git log --oneline -3

# Force push (if needed)
git push origin main --force

# Check remote
git remote -v

# Create empty commit to trigger deployment
git commit --allow-empty -m "Trigger deployment"
git push origin main
```

## 📞 **Support**

If the issue persists:
1. Check Vercel status page: [status.vercel.com](https://status.vercel.com)
2. Contact Vercel support
3. Check GitHub repository permissions
4. Verify environment variables are correct

## ✅ **Expected Result**

After successful deployment:
- Project appears in Vercel Dashboard
- New deployments show in the Deployments tab
- Website is accessible at `https://agrisahayak.vercel.app`
- Health endpoint returns: `{"status": "healthy", "database": "connected"}` 