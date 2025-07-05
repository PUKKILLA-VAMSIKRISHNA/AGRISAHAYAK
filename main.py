import os
import logging
from flask import Flask, jsonify
from dotenv import load_dotenv
import re

# Import extensions
from extensions import db, login_manager, mail, migrate

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = os.environ.get('SECRET_KEY', 'Vamsi@123')

# Configure the database
def get_database_url():
    # First try to get the DATABASE_URL from environment
    database_url = os.environ.get('DATABASE_URL')
    
    print(f"Original DATABASE_URL: {database_url}")
    
    # If DATABASE_URL is not set or is invalid, use the default local database
    if not database_url or not database_url.startswith(('postgres://', 'postgresql://')):
        print("No valid DATABASE_URL found, using local database")
        database_url = "postgresql://postgres:Vamsi123@localhost:5432/agrisahayak"
        return database_url
    
    # Convert postgres:// to postgresql:// if needed (required for newer psycopg2 versions)
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    # Additional validation for Supabase URLs
    if 'supabase.co' in database_url:
        print("Detected Supabase URL, attempting to fix parsing issues")
        try:
            from urllib.parse import urlparse, quote_plus
            
            # Handle the case where the URL might be malformed
            if '@' in database_url and '://' in database_url:
                # Extract the parts manually if urlparse fails
                protocol_part = database_url.split('://')[0] + '://'
                rest_part = database_url.split('://')[1]
                
                if '@' in rest_part:
                    auth_part = rest_part.split('@')[0]
                    host_part = rest_part.split('@')[1]
                    
                    if ':' in auth_part:
                        username = auth_part.split(':')[0]
                        password = ':'.join(auth_part.split(':')[1:])  # Handle passwords with colons
                        # Don't quote_plus the password as it might cause issues
                        password = password
                    else:
                        username = auth_part
                        password = ''
                    
                    if ':' in host_part:
                        hostname = host_part.split(':')[0]
                        port_db_part = host_part.split(':')[1]
                        if '/' in port_db_part:
                            port = port_db_part.split('/')[0]
                            database = port_db_part.split('/')[1]
                        else:
                            port = '5432'
                            database = port_db_part
                    else:
                        hostname = host_part.split('/')[0]
                        database = host_part.split('/')[1] if '/' in host_part else 'postgres'
                        port = '5432'
                    
                    # Rebuild the URL
                    database_url = f"postgresql://{username}:{password}@{hostname}:{port}/{database}"
                    print(f"Fixed Supabase URL: {database_url}")
                else:
                    print("Could not parse Supabase URL, using fallback")
                    database_url = "postgresql://postgres:Vamsi123@localhost:5432/agrisahayak"
            else:
                print("Invalid URL format, using fallback")
                database_url = "postgresql://postgres:Vamsi123@localhost:5432/agrisahayak"
                
        except Exception as e:
            print(f"Error parsing Supabase URL: {e}")
            # Fallback to local database
            database_url = "postgresql://postgres:Vamsi123@localhost:5432/agrisahayak"
    
    # For Vercel deployment, if we can't connect to Supabase, use a fallback
    if 'supabase.co' in database_url and os.environ.get('VERCEL'):
        print("Running on Vercel with Supabase - will attempt connection but may fail gracefully")
        # Add additional parameters for Vercel + Supabase compatibility
        if '?' not in database_url:
            database_url += "?sslmode=require"
        else:
            database_url += "&sslmode=require"
    
    print(f"Final DATABASE_URL: {database_url}")
    return database_url

# Try to get database URL, but don't fail if it's not available
try:
    print(f"Environment check - VERCEL: {os.environ.get('VERCEL')}")
    print(f"Environment check - DATABASE_URL exists: {bool(os.environ.get('DATABASE_URL'))}")
    print(f"Environment check - SECRET_KEY exists: {bool(os.environ.get('SECRET_KEY'))}")
    
    database_url = get_database_url()
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "pool_timeout": 5,
        "max_overflow": 0,
        "pool_size": 1,
        "connect_args": {
            "sslmode": "require",  # Force SSL for Supabase
            "connect_timeout": 10,
            "application_name": "agrisahayak_app"
        }
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
except Exception as e:
    print(f"Error configuring database: {e}")
    # Use a dummy database URL that will fail gracefully
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_DEBUG'] = True
app.config['MAIL_SUPPRESS_SEND'] = False
app.config['MAIL_MAX_EMAILS'] = None
app.config['MAIL_ASCII_ATTACHMENTS'] = False
app.config['MAIL_TIMEOUT'] = 30
app.config['MAIL_USE_CREDENTIALS'] = True
app.config['MAIL_FAIL_SILENTLY'] = False
app.config['BASE_URL'] = os.getenv('BASE_URL', 'http://localhost:5000')

# Initialize extensions with app
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
mail.init_app(app)
migrate.init_app(app, db)

# API keys
app.config['GEMINI_API_KEY'] = os.environ.get("GEMINI_API_KEY", "")
app.config['YOUTUBE_API_KEY'] = os.environ.get("YOUTUBE_API_KEY", "")
app.config['WEATHER_API_KEY'] = os.environ.get("WEATHER_API_KEY", "")

# Do NOT import models here

# Do NOT call init_db() here

# Import routes at the end
from routes import *

# Import models and migrations after db and app are initialized
def setup_app(app):
    with app.app_context():
        # Try to initialize database, but don't crash if it fails
        db_initialized = False
        try:
            import models
            from migrations import init_db
            
            # Test database connection first with retry
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    print(f"Attempting database connection (attempt {attempt + 1}/{max_retries})...")
                    connection = db.engine.connect()
                    connection.close()
                    print("Database connection successful")
                    break
                except Exception as conn_error:
                    print(f"Database connection test failed (attempt {attempt + 1}): {conn_error}")
                    print(f"Connection error type: {type(conn_error).__name__}")
                    if hasattr(conn_error, 'orig'):
                        print(f"Original error: {conn_error.orig}")
                    
                    if attempt == max_retries - 1:
                        raise conn_error
                    else:
                        print("Retrying in 2 seconds...")
                        import time
                        time.sleep(2)
            
            init_db(app, db)
            print("Database initialized successfully")
            db_initialized = True
        except Exception as e:
            print(f"Database initialization failed: {e}")
            print("App will continue without database functionality")
            db_initialized = False
        
        # Store database status in app config
        app.config['DB_INITIALIZED'] = db_initialized
        
        # Set up user loader with error handling
        from models import User
        @login_manager.user_loader
        def load_user(user_id):
            if not db_initialized:
                return None
            try:
                return User.query.get(int(user_id))
            except Exception as e:
                print(f"Error loading user: {e}")
                return None
        
        # Register routes directly - only if database is available
        if db_initialized:
            app.add_url_rule('/login', 'login', login, methods=['GET', 'POST'])
            app.add_url_rule('/register', 'register', register, methods=['GET', 'POST'])
            app.add_url_rule('/verify_email/<email>', 'verify_email', verify_email, methods=['GET', 'POST'])
            app.add_url_rule('/resend_otp/<email>', 'resend_otp', resend_otp)
            app.add_url_rule('/forgot_password', 'forgot_password', forgot_password, methods=['GET', 'POST'])
            app.add_url_rule('/reset_password/<token>', 'reset_password', reset_password, methods=['GET', 'POST'])
        else:
            # Add placeholder routes that return maintenance message
            def maintenance_route():
                return """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>AgriSahayak - Maintenance</title>
                    <meta charset="utf-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <style>
                        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                        .container { max-width: 600px; margin: 0 auto; }
                        .status { color: #666; margin: 20px 0; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>🌾 AgriSahayak</h1>
                        <div class="status">
                            <p>Database is currently unavailable.</p>
                            <p>Please try again later.</p>
                        </div>
                    </div>
                </body>
                </html>
                """
            
            app.add_url_rule('/login', 'login', maintenance_route, methods=['GET', 'POST'])
            app.add_url_rule('/register', 'register', maintenance_route, methods=['GET', 'POST'])
            app.add_url_rule('/verify_email/<email>', 'verify_email', maintenance_route, methods=['GET', 'POST'])
            app.add_url_rule('/resend_otp/<email>', 'resend_otp', maintenance_route)
            app.add_url_rule('/forgot_password', 'forgot_password', maintenance_route, methods=['GET', 'POST'])
            app.add_url_rule('/reset_password/<token>', 'reset_password', maintenance_route, methods=['GET', 'POST'])
        
        # Apply login_required decorator to protected routes
        from functools import wraps
        from flask_login import login_required
        
        # Create protected versions of the functions
        protected_logout = login_required(logout)
        protected_dashboard = login_required(dashboard)
        protected_chat = login_required(chat)
        protected_new_chat = login_required(new_chat)
        protected_send_message = login_required(send_message)
        protected_delete_chat = login_required(delete_chat)
        protected_api_get_crop_recommendations = login_required(api_get_crop_recommendations)
        protected_api_get_youtube_videos = login_required(api_get_youtube_videos)
        protected_api_translate = login_required(api_translate)
        protected_api_text_to_speech = login_required(api_text_to_speech)
        protected_api_speech_to_text = login_required(api_speech_to_text)
        protected_profile = login_required(profile)
        
        # Register protected routes - only if database is available
        if db_initialized:
            app.add_url_rule('/logout', 'logout', protected_logout)
            app.add_url_rule('/dashboard', 'dashboard', protected_dashboard)
            app.add_url_rule('/chat/<int:chat_id>', 'chat', protected_chat)
            app.add_url_rule('/chat/new', 'new_chat', protected_new_chat)
            app.add_url_rule('/api/send_message', 'send_message', protected_send_message, methods=['POST'])
            app.add_url_rule('/api/delete_chat/<int:chat_id>', 'delete_chat', protected_delete_chat, methods=['DELETE'])
            app.add_url_rule('/api/get_crop_recommendations', 'api_get_crop_recommendations', protected_api_get_crop_recommendations, methods=['POST'])
            app.add_url_rule('/api/get_youtube_videos', 'api_get_youtube_videos', protected_api_get_youtube_videos, methods=['POST'])
            app.add_url_rule('/api/translate', 'api_translate', protected_api_translate, methods=['POST'])
            app.add_url_rule('/api/text_to_speech', 'api_text_to_speech', protected_api_text_to_speech, methods=['POST'])
            app.add_url_rule('/api/speech_to_text', 'api_speech_to_text', protected_api_speech_to_text, methods=['POST'])
            app.add_url_rule('/profile', 'profile', protected_profile, methods=['GET', 'POST'])
        else:
            # Add placeholder routes for protected routes
            app.add_url_rule('/logout', 'logout', maintenance_route)
            app.add_url_rule('/dashboard', 'dashboard', maintenance_route)
            app.add_url_rule('/chat/<int:chat_id>', 'chat', maintenance_route)
            app.add_url_rule('/chat/new', 'new_chat', maintenance_route)
            app.add_url_rule('/api/send_message', 'send_message', maintenance_route, methods=['POST'])
            app.add_url_rule('/api/delete_chat/<int:chat_id>', 'delete_chat', maintenance_route, methods=['DELETE'])
            app.add_url_rule('/api/get_crop_recommendations', 'api_get_crop_recommendations', maintenance_route, methods=['POST'])
            app.add_url_rule('/api/get_youtube_videos', 'api_get_youtube_videos', maintenance_route, methods=['POST'])
            app.add_url_rule('/api/translate', 'api_translate', maintenance_route, methods=['POST'])
            app.add_url_rule('/api/text_to_speech', 'api_text_to_speech', maintenance_route, methods=['POST'])
            app.add_url_rule('/api/speech_to_text', 'api_speech_to_text', maintenance_route, methods=['POST'])
            app.add_url_rule('/profile', 'profile', maintenance_route, methods=['GET', 'POST'])
        
        # Add a simple health check route that doesn't require database
        def health_check():
            return jsonify({
                'status': 'healthy',
                'database': 'connected' if app.config.get('DB_INITIALIZED', False) else 'disconnected',
                'database_url_set': bool(os.environ.get('DATABASE_URL')),
                'message': 'AgriSahayak is running'
            })
        
        app.add_url_rule('/health', 'health_check', health_check)
        
        # Add a database status check route
        def db_status():
            db_url = os.environ.get('DATABASE_URL', 'Not set')
            db_initialized = app.config.get('DB_INITIALIZED', False)
            
            status_info = {
                'database_url_set': bool(db_url and db_url != 'Not set'),
                'database_initialized': db_initialized,
                'environment': 'vercel' if os.environ.get('VERCEL') else 'local',
                'message': 'Database status check'
            }
            
            if db_initialized:
                status_info['status'] = 'connected'
                status_info['message'] = 'Database is connected and working'
            else:
                status_info['status'] = 'disconnected'
                status_info['message'] = 'Database is not connected'
                if not db_url or db_url == 'Not set':
                    status_info['error'] = 'DATABASE_URL environment variable not set'
                else:
                    status_info['error'] = 'Database connection failed'
            
            return jsonify(status_info)
        
        app.add_url_rule('/db-status', 'db_status', db_status)
        
        # Add favicon route
        def favicon():
            # Return a simple 1x1 transparent PNG as favicon
            from flask import Response
            import base64
            
            # Simple 1x1 transparent PNG
            png_data = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==')
            
            response = Response(png_data, mimetype='image/png')
            response.headers['Cache-Control'] = 'public, max-age=31536000'
            return response
        
        app.add_url_rule('/favicon.ico', 'favicon', favicon)
        app.add_url_rule('/favicon.png', 'favicon_png', favicon)  # Handle .png requests too
        
        # Add static file routes for Vercel
        def serve_static_file(filename):
            return app.send_static_file(filename)
        
        app.add_url_rule('/static/<path:filename>', 'static_file', serve_static_file)
        
        # Add a simple index route that doesn't require database
        def simple_index():
            if not app.config.get('DB_INITIALIZED', False):
                # Return a simple HTML response instead of JSON
                return """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>AgriSahayak - Starting Up</title>
                    <meta charset="utf-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <style>
                        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                        .container { max-width: 600px; margin: 0 auto; }
                        .status { color: #666; margin: 20px 0; }
                        .retry { margin-top: 30px; }
                        .retry a { color: #007bff; text-decoration: none; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>🌾 AgriSahayak</h1>
                        <div class="status">
                            <p>Application is starting up...</p>
                            <p>Database: Connecting...</p>
                            <p>Status: Initializing</p>
                        </div>
                        <div class="retry">
                            <a href="/">Refresh Page</a>
                        </div>
                    </div>
                </body>
                </html>
                """
            return index()  # Use the original index function if database is available
        
        app.add_url_rule('/', 'index', simple_index)
        
        # Add a catch-all route for any other requests
        def catch_all(path):
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>AgriSahayak - Page Not Found</title>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                    .container { max-width: 600px; margin: 0 auto; }
                    .status { color: #666; margin: 20px 0; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🌾 AgriSahayak</h1>
                    <div class="status">
                        <p>Page not found: /{}</p>
                        <p><a href="/">Go to Home</a></p>
                    </div>
                </div>
            </body>
            </html>
            """.format(path), 404
        
        app.add_url_rule('/<path:path>', 'catch_all', catch_all)

setup_app(app)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
