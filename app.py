import os
import logging
from flask import Flask
from dotenv import load_dotenv
import re

# Import extensions
from extensions import db, login_manager, mail, migrate

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__, static_folder='public', static_url_path='/static')
app.secret_key = os.environ.get('SECRET_KEY', 'Vamsi@123')

# Configure the database
def get_database_url():
    # First try to get the DATABASE_URL from environment
    database_url = os.environ.get('DATABASE_URL')
    
    # If DATABASE_URL is not set or is invalid, use the default local database
    if not database_url or not database_url.startswith(('postgres://', 'postgresql://')):
        database_url = "postgresql://postgres:Vamsi123@localhost:5432/agrisahayak"
    
    # Convert postgres:// to postgresql:// if needed (required for newer psycopg2 versions)
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    # Additional validation for Supabase URLs
    if 'supabase.co' in database_url:
        # Ensure proper URL encoding for special characters in password
        try:
            from urllib.parse import urlparse, urlunparse, quote_plus
            parsed = urlparse(database_url)
            
            # Reconstruct the URL with proper encoding
            username = parsed.username
            password = quote_plus(parsed.password) if parsed.password else ''
            hostname = parsed.hostname
            port = parsed.port or 5432
            database = parsed.path.lstrip('/')
            
            # Rebuild the URL
            database_url = f"postgresql://{username}:{password}@{hostname}:{port}/{database}"
            
        except Exception as e:
            print(f"Error parsing database URL: {e}")
            # Fallback to local database
            database_url = "postgresql://postgres:Vamsi123@localhost:5432/agrisahayak"
    
    return database_url

app.config["SQLALCHEMY_DATABASE_URI"] = get_database_url()
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
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

# Import models after db initialization
with app.app_context():
    try:
        import models
        from migrations import init_db
        init_db(app, db)
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization failed: {e}")
        # Continue without database for now
    
    @login_manager.user_loader
    def load_user(user_id):
        try:
            return models.User.query.get(int(user_id))
        except Exception as e:
            print(f"Error loading user: {e}")
            return None

# Import routes after app initialization to avoid circular imports
# Note: routes are imported directly in main.py, so we don't need init_routes here

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
