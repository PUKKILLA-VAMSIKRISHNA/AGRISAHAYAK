# Vercel Deployment Fix Guide

## Issue Analysis
The chat and voice functionalities are not working in your Vercel deployment because:
1. **Static files are not being served properly** (404 errors) - **MAIN ISSUE**
2. Environment variables may not be properly set in Vercel
3. Database connection issues
4. API keys are missing

## Step 1: Set Environment Variables in Vercel

Go to your Vercel dashboard and set these environment variables:

### Required Environment Variables:
```
DATABASE_URL=postgresql://postgres:VamsiKrishna123@db.scwrkxpsdwtehckqbjht.supabase.co:5432/postgres
SECRET_KEY=Vamsi@123
BASE_URL=https://agrisahayak.vercel.app
```

### Optional but Recommended:
```
GEMINI_API_KEY=your_gemini_api_key_here
YOUTUBE_API_KEY=your_youtube_api_key_here
WEATHER_API_KEY=your_weather_api_key_here
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_gmail_app_password
```

## Step 2: Update Vercel Configuration

Update your `vercel.json` to handle environment variables better:

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
    { "src": "/static/(.*)", "dest": "/static/$1" },
    { "src": "/favicon.ico", "dest": "/static/images/favicon.ico" },
    { "src": "/favicon.png", "dest": "/static/images/favicon.ico" },
    { "src": "/(.*)", "dest": "/main.py" }
  ],
  "env": {
    "PYTHONPATH": ".",
    "FLASK_ENV": "production"
  }
}
```

## Step 3: Test Database Connection

After setting environment variables, test the database connection:

1. Go to your Vercel deployment URL
2. Visit `/health` endpoint
3. Check if database status shows "connected"

## Step 4: Debug Steps

If issues persist:

1. **Check Vercel Logs**: Go to your Vercel dashboard → Functions → Check deployment logs
2. **Test API Endpoints**: Use browser dev tools to check network requests
3. **Verify Environment Variables**: Ensure all variables are set correctly

## Step 5: Common Issues and Solutions

### Issue: Database Connection Fails
- **Solution**: Ensure DATABASE_URL is correctly set with SSL parameters
- **Alternative**: Add `?sslmode=require` to your DATABASE_URL

### Issue: Chat Not Responding
- **Solution**: Check if GEMINI_API_KEY is set
- **Debug**: Open browser console and check for JavaScript errors

### Issue: Voice Not Working
- **Solution**: Ensure HTTPS is enabled (required for microphone access)
- **Debug**: Check browser console for Web Speech API errors

## Step 6: Manual Environment Variable Setup

In Vercel Dashboard:
1. Go to your project
2. Click "Settings"
3. Go to "Environment Variables"
4. Add each variable:
   - Name: `DATABASE_URL`
   - Value: `postgresql://postgres:VamsiKrishna123@db.scwrkxpsdwtehckqbjht.supabase.co:5432/postgres`
   - Environment: Production, Preview, Development
5. Repeat for all other variables

## Step 7: Redeploy

After setting environment variables:
1. Go to Vercel dashboard
2. Click "Redeploy" on your latest deployment
3. Wait for deployment to complete
4. Test the functionality

## Step 8: Verification

Test these endpoints after deployment:
- `/health` - Should show database connected
- `/chat/new` - Should create new chat
- `/api/send_message` - Should respond to messages (requires login)

## Troubleshooting

If you still have issues:
1. Check Vercel function logs for errors
2. Verify all environment variables are set
3. Ensure database is accessible from Vercel's servers
4. Check if any API keys are expired or invalid 