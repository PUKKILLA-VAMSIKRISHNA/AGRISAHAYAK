from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
from flask_mail import Mail
from flask_migrate import Migrate

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
mail = Mail()
migrate = Migrate()

app = Flask(__name__)
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
