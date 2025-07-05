def init_db(app, db):
    try:
        from models import User, Chat, Message, UserProfile, EmailVerification, PasswordReset  # Import inside the function
        with app.app_context():
            # Create all tables
            db.create_all()
            print("Database tables created successfully!")
    except Exception as e:
        print(f"Error creating database tables: {e}")
        raise e 
