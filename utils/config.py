import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    API_BASE_URL = os.getenv('API_BASE_URL', 'http://127.0.0.1:5000')