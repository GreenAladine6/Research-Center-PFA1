from datetime import timedelta
import os
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify, make_response, current_app
from flask_jwt_extended import (
    create_access_token,
    set_access_cookies,
    unset_jwt_cookies,
    JWTManager
)
from werkzeug.security import check_password_hash
from Database.db import JSONDatabase

# Load environment variables
load_dotenv()

# Create Blueprint for authentication
auth_bp = Blueprint('auth', __name__)

# Initialize JWT
jwt = JWTManager()

# Get credentials from environment variables
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME').strip()
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD').strip()

@auth_bp.post('/login')
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'Invalid request'}), 400

        username = data.get('username', '').strip()
        password = data.get('password', '')

        # Admin authentication
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            token = create_access_token(
                identity={
                    'username': username,
                    'role': 'admin',
                    'name': 'Administrator'
                }
            )
            response = make_response(jsonify({
                'message': 'Admin login successful',
                'redirect': '/dashboard/projects'
            }))
            set_access_cookies(response, token)
            return response

        # User authentication
        db = JSONDatabase()
        user = db.find_researcher_by_email(username)
        
        if user and check_password_hash(user.get('PASSWORD', ''), password):
            token = create_access_token(
                identity={
                    'username': user['EMAIL'],
                    'role': 'user',
                    'name': user['FULL_NAME'],
                    'user_id': user['id']
                }
            )
            response = make_response(jsonify({
                'message': 'User login successful',
                'redirect': '/dashboard/user'
            }))
            set_access_cookies(response, token)
            return response

        return jsonify({'message': 'Invalid username or password'}), 401

    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 500

@auth_bp.post('/logout')
def logout():
    response = make_response(jsonify({'message': 'Logout successful'}))
    unset_jwt_cookies(response)
    return response