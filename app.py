from flask import Flask, redirect, render_template, url_for
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dashboard.dashboard import dashboard_bp
from api.project import projects_bp
from api.events import events_bp
from api.auth import auth_bp
from api.researchers import researchers_bp
from api.publications import publications_bp
from fr.fr import fr_bp
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

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False  # Enable for production

# Initialize JWTManager after Flask app
jwt = JWTManager(app)

# Initialize database
db = JSONDatabase()
app.config.from_object(Config)

# Register blueprints
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(projects_bp, url_prefix='/api/project')
app.register_blueprint(events_bp, url_prefix='/api/events')
app.register_blueprint(fr_bp, url_prefix='/')
app.register_blueprint(researchers_bp, url_prefix='/api/researcher')
app.register_blueprint(publications_bp, url_prefix='/api/publication')
from flask import send_from_directory




@app.template_filter('datetimeformat')
def datetimeformat(value, format='%Y-%m-%d %H:%M:%S'):
    if isinstance(value, str):
        # Convertir la chaîne ISO en objet datetime
        value = datetime.fromisoformat(value)
    return value.strftime(format)

if __name__ == '__main__':
    app.run(debug=True)