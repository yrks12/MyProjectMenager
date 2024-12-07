# app/__init__.py
from flask import Flask, render_template, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from os import getenv
import logging
from logging.handlers import RotatingFileHandler

load_dotenv()

SQLALCHEMY_DATABASE_URI = getenv("SQLALCHEMY_DATABASE_URI")

# Initialize Flask app
app = Flask(__name__)

# Configure logging
if not app.debug:
    # Set up a file handler to log messages to a file
    file_handler = RotatingFileHandler('app.log', maxBytes=10240, backupCount=10)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    app.logger.addHandler(file_handler)

    # Log that the application has started
    app.logger.info('MyProjectManager startup')

# Load configuration
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI

# Set the secret key for session management
app.secret_key = 'your_secret_key_here'  # Replace with a strong random key

# Initialize database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Import models so that Flask-Migrate can detect them
from app.models import Project, Task  # Add this line

# Import routes
from app.routes import project_routes, task_routes

app.register_blueprint(project_routes)
app.register_blueprint(task_routes)