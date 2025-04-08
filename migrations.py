from app import app, db
from models import User, Chat, Message, UserProfile, EmailVerification

def init_db():
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!") 
