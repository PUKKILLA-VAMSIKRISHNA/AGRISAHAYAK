# AgriSahayak - AI-Powered Agricultural Assistant

A comprehensive web application that provides AI-powered agricultural assistance to farmers, featuring multilingual support, weather data, crop recommendations, and interactive chat functionality.

## Features

- 🤖 AI-powered agricultural chatbot using Google Gemini
- 🌍 Multilingual support (English, Hindi, Tamil, Telugu, and more)
- 🌤️ Real-time weather data integration
- 📹 YouTube video recommendations for farming techniques
- 🎤 Voice-to-text and text-to-speech capabilities
- 📧 Email verification and password reset functionality
- 📱 Responsive design for mobile and desktop

## Tech Stack

- **Backend**: Flask, Python
- **Database**: PostgreSQL (Supabase)
- **AI**: Google Gemini API
- **Authentication**: Flask-Login
- **Email**: Flask-Mail
- **Deployment**: Vercel

## Local Development

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables (see `.env.example`)
4. Run the application: `python main.py`

## Environment Variables

Create a `.env` file with the following variables:

```env
SECRET_KEY=your_secret_key
DATABASE_URL=your_supabase_database_url
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_email_app_password
GEMINI_API_KEY=your_gemini_api_key
YOUTUBE_API_KEY=your_youtube_api_key
WEATHER_API_KEY=your_weather_api_key
BASE_URL=http://localhost:5000
```

## Vercel Deployment

### Prerequisites

1. **Supabase Database**: Set up a PostgreSQL database on Supabase
2. **API Keys**: Obtain API keys for Gemini, YouTube, and Weather APIs
3. **Email Service**: Configure Gmail with app password

### Deployment Steps

1. **Connect to Vercel**:
   - Install Vercel CLI: `npm i -g vercel`
   - Login: `vercel login`
   - Deploy: `vercel`

2. **Set Environment Variables in Vercel**:
   - Go to your Vercel project dashboard
   - Navigate to Settings > Environment Variables
   - Add all required environment variables

3. **Database Configuration**:
   - Ensure your Supabase DATABASE_URL is properly formatted
   - The URL should be: `postgresql://username:password@host:port/database`
   - If using Supabase, the URL format is: `postgresql://postgres:[password]@[host]:5432/postgres`

### Troubleshooting

#### Database Connection Issues

If you encounter database connection errors:

1. **Check DATABASE_URL format**: Ensure it starts with `postgresql://`
2. **Verify Supabase credentials**: Check username, password, and host
3. **Test connection**: Use a database client to verify connectivity
4. **Check Vercel logs**: Monitor deployment logs for specific errors

#### Common Error: "could not translate host name"

This error occurs when the DATABASE_URL is malformed. The application now includes automatic URL parsing and fallback mechanisms.

#### Health Check

After deployment, test the health endpoint:
```
https://your-app.vercel.app/health
```

This will show the application status and database connection state.

## API Endpoints

- `GET /` - Home page
- `GET /health` - Health check endpoint
- `POST /login` - User login
- `POST /register` - User registration
- `GET /dashboard` - User dashboard (requires authentication)
- `POST /api/send_message` - Send chat message
- `POST /api/get_crop_recommendations` - Get crop recommendations
- `POST /api/translate` - Translate text
- `POST /api/text_to_speech` - Convert text to speech
- `POST /api/speech_to_text` - Convert speech to text

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please open an issue on GitHub or contact the development team. 