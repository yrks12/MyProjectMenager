# app/__init__.py
from flask import Flask, render_template, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from os import getenv

load_dotenv()

SQLALCHEMY_DATABASE_URI = getenv("SQLALCHEMY_DATABASE_URI")

# Initialize Flask app
app = Flask(__name__)

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