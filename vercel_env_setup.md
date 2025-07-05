# Vercel Environment Variables Setup

## **CRITICAL: Set these environment variables in Vercel Dashboard**

### Step 1: Go to Vercel Dashboard
1. Visit [vercel.com](https://vercel.com)
2. Sign in to your account
3. Select your `agrisahayak` project

### Step 2: Add Environment Variables
1. Click on **Settings** tab
2. Go to **Environment Variables** section
3. Click **Add** for each variable below

### Step 3: Add These Variables

#### **Required Variables:**

**1. DATABASE_URL**
- **Name:** `DATABASE_URL`
- **Value:** `postgresql://postgres:VamsiKrishna123@db.scwrkxpsdwtehckqbjht.supabase.co:5432/postgres`
- **Environment:** Production, Preview, Development

**2. SECRET_KEY**
- **Name:** `SECRET_KEY`
- **Value:** `Vamsi@123`
- **Environment:** Production, Preview, Development

**3. BASE_URL**
- **Name:** `BASE_URL`
- **Value:** `https://agrisahayak.vercel.app`
- **Environment:** Production, Preview, Development

**4. GEMINI_API_KEY**
- **Name:** `GEMINI_API_KEY`
- **Value:** `AIzaSyAJgpiQdsw8LmH8z2IbcUP0d4zZcPAJBhE`
- **Environment:** Production, Preview, Development

#### **Optional Variables (for full functionality):**

**5. YOUTUBE_API_KEY**
- **Name:** `YOUTUBE_API_KEY`
- **Value:** `your_youtube_api_key_here`
- **Environment:** Production, Preview, Development

**6. WEATHER_API_KEY**
- **Name:** `WEATHER_API_KEY`
- **Value:** `your_weather_api_key_here`
- **Environment:** Production, Preview, Development

**7. MAIL_USERNAME**
- **Name:** `MAIL_USERNAME`
- **Value:** `your_email@gmail.com`
- **Environment:** Production, Preview, Development

**8. MAIL_PASSWORD**
- **Name:** `MAIL_PASSWORD`
- **Value:** `your_gmail_app_password`
- **Environment:** Production, Preview, Development

### Step 4: Save and Redeploy
1. Click **Save** for each variable
2. Go to **Deployments** tab
3. Click **Redeploy** on your latest deployment
4. Wait for deployment to complete

### Step 5: Test
After redeployment, test these URLs:
- `https://agrisahayak.vercel.app/health` - Should show database connected
- `https://agrisahayak.vercel.app/static/js/chat.js` - Should load JavaScript file
- `https://agrisahayak.vercel.app/static/css/style.css` - Should load CSS file

### Troubleshooting
If static files still don't load:
1. Check Vercel function logs
2. Ensure all environment variables are set
3. Try accessing static files directly via URL
4. Check browser console for errors

## **IMPORTANT NOTES:**
- Make sure to set **Environment** to "Production, Preview, Development" for all variables
- The GEMINI_API_KEY is crucial for chat functionality
- The DATABASE_URL is crucial for user authentication and chat history
- After setting variables, you MUST redeploy for changes to take effect 