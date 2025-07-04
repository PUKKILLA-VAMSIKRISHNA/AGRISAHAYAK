from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:Vamsi123@localhost:5432/agrisahayak"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

def clear_all_user_data():
    with app.app_context():
        try:
            # Execute raw SQL to truncate all tables
            db.session.execute(text('TRUNCATE TABLE message, chat, user_profile, email_verification, "user" CASCADE'))
            db.session.commit()
            print("All user data has been successfully cleared from the database.")
        except Exception as e:
            db.session.rollback()
            print(f"Error occurred: {str(e)}")
            print("No changes were made to the database.")

if __name__ == "__main__":
    clear_all_user_data() 