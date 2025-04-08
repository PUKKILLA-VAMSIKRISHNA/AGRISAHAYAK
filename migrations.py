from app import app, db, migrate
from models import User, Chat, Message, UserProfile, EmailVerification

def init_db():
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Initialize Flask-Migrate
        migrate.init_app(app, db)
        
        print("Database tables created successfully!") 
