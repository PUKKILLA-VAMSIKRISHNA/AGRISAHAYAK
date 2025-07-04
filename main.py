import os
import logging
from flask import Flask
from dotenv import load_dotenv

# Import extensions
from extensions import db, login_manager, mail, migrate

app = Flask(__name__)

# Add database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:Vamsi123@localhost:5432/agrisahayak"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ... config ...

db.init_app(app)
login_manager.init_app(app)
mail.init_app(app)
migrate.init_app(app, db)

# Do NOT import models here

# Do NOT call init_db() here

# Import routes at the end
from routes import *

# Import models and migrations after db and app are initialized
def setup_app(app):
    with app.app_context():
        import models
        from migrations import init_db
        init_db()
        
        from models import User
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

setup_app(app)

app = app
