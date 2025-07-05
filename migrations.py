def init_db(app, db):
    from models import User, Chat, Message, UserProfile, EmailVerification  # Import inside the function
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!") 
