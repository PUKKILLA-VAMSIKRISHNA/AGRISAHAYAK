# Vercel Deployment Guide for AgriSahayak

## Quick Deployment Steps

### 1. Prepare Your Environment Variables

Before deploying, ensure you have all the required environment variables:

```bash
# Required Environment Variables for Vercel
SECRET_KEY=your_secure_secret_key
DATABASE_URL=postgresql://postgres:password@host:5432/postgres
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_gmail_app_password
GEMINI_API_KEY=your_gemini_api_key
YOUTUBE_API_KEY=your_youtube_api_key
WEATHER_API_KEY=your_weather_api_key
BASE_URL=https://your-app.vercel.app
```

### 2. Deploy to Vercel

#### Option A: Using Vercel CLI
```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy
vercel

# Follow the prompts to set up your project
```

#### Option B: Using Vercel Dashboard
1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import your GitHub repository
4. Configure the project settings
5. Add environment variables
6. Deploy

### 3. Set Environment Variables in Vercel

1. Go to your Vercel project dashboard
2. Navigate to **Settings** > **Environment Variables**
3. Add each environment variable:
   - `SECRET_KEY`
   - `DATABASE_URL`
   - `MAIL_USERNAME`
   - `MAIL_PASSWORD`
   - `GEMINI_API_KEY`
   - `YOUTUBE_API_KEY`
   - `WEATHER_API_KEY`
   - `BASE_URL`

### 4. Database Setup (Supabase)

1. Create a Supabase project at [supabase.com](https://supabase.com)
2. Get your database connection string
3. Format: `postgresql://postgres:[password]@[host]:5432/postgres`
4. Add to Vercel environment variables as `DATABASE_URL`

### 5. Test Your Deployment

After deployment, test these endpoints:

```bash
# Health check
curl https://your-app.vercel.app/health

# Should return:
{
  "status": "healthy",
  "database": "connected",
  "message": "AgriSahayak is running"
}
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check DATABASE_URL format
   - Ensure Supabase credentials are correct
   - Verify network connectivity

2. **Environment Variables Not Set**
   - Double-check all variables in Vercel dashboard
   - Ensure no typos in variable names

3. **Import Errors**
   - Check requirements.txt for all dependencies
   - Ensure Python version compatibility

### Debugging Steps

1. **Check Vercel Logs**
   - Go to your project dashboard
   - Click on "Functions" tab
   - Check deployment logs

2. **Test Health Endpoint**
   - Visit `/health` endpoint
   - Check database connection status

3. **Verify Environment Variables**
   - Use Vercel CLI: `vercel env ls`
   - Check dashboard settings

## Post-Deployment

1. **Set up custom domain** (optional)
2. **Configure email service** for user verification
3. **Test all features**:
   - User registration
   - Chat functionality
   - Weather data
   - Crop recommendations

## Support

If you encounter issues:
1. Check Vercel deployment logs
2. Verify all environment variables
3. Test database connectivity
4. Open an issue on GitHub 