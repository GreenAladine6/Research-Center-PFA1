from flask import Flask, redirect
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dashboard.dashboard import dashboard_bp
from api.project import projects_bp
from api.auth import auth_bp
from utils.config import Config
from Database.db import JSONDatabase

from datetime import datetime


import os
from dotenv import load_dotenv




# Load environment variables
load_dotenv()

# Create Flask app instance
app = Flask(__name__)
CORS(app)

# Set JWT configuration
app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY')  # Set JWT secret key
app.config['JWT_TOKEN_LOCATION'] = ['cookies']  # Store tokens in cookies

# Initialize JWTManager after Flask app
jwt = JWTManager(app)

# Initialize database
db = JSONDatabase()
app.config.from_object(Config)

# Register blueprints
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(projects_bp, url_prefix='/api/project')





@app.template_filter('datetimeformat')
def datetimeformat(value, format='%Y-%m-%d %H:%M:%S'):
    if isinstance(value, str):
        # Convertir la chaîne ISO en objet datetime
        value = datetime.fromisoformat(value)
    return value.strftime(format)

if __name__ == '__main__':
    app.run(debug=True)