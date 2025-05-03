from datetime import timedelta
import os
import bcrypt
import logging
from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import create_access_token, set_access_cookies
from Database.db import JSONDatabase

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

# Environment variables
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
db = JSONDatabase()

def validate_hash(hashed_str: str) -> bool:
    """Validate if a string is a valid bcrypt hash."""
    try:
        bcrypt.checkpw(b"test", hashed_str.encode())  # Just check format
        return True
    except (ValueError, TypeError):
        return False

@auth_bp.post('/login')
def login():
    data = request.json
    if not data:
        return jsonify({'message': 'Invalid request'}), 400

    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()
    
    if not username or not password:
        return jsonify({'message': 'Credentials required'}), 400

    try:
        # Admin login
        if username == ADMIN_USERNAME:
            if password == ADMIN_PASSWORD:
                token = create_access_token(
                    identity=username,
                    additional_claims={'role': 'admin'},
                    expires_delta=timedelta(hours=3))
                response = make_response(jsonify({'message': 'Admin login successful'}))
                set_access_cookies(response, token)
                return response
            return jsonify({'message': 'Invalid admin credentials'}), 401

        # Researcher login
        researchers = db.select_filter("RESEARCHER", {"EMAIL": username.lower().strip()})
        if not researchers:
            logger.warning(f"No researcher found for email: {username}")
            return jsonify({'message': 'Invalid credentials'}), 401

        researcher = researchers[0]
        stored_hash = researcher.get('PASSWORD', '')
        
        # Debug logging
        logger.debug(f"Attempting login for: {username}")
        logger.debug(f"Stored hash: {stored_hash}")
        logger.debug(f"Hash validation: {validate_hash(stored_hash)}")

        if not validate_hash(stored_hash):
            logger.error("Invalid hash format in database")
            return jsonify({'message': 'Authentication error'}), 500

        password_bytes = password.encode('utf-8')
        stored_hash_bytes = stored_hash.encode('utf-8')

        if not bcrypt.checkpw(password_bytes, stored_hash_bytes):
            logger.warning(f"Password mismatch for: {username}")
            return jsonify({'message': 'Invalid password'}), 401

        # Create token
        token = create_access_token(
            identity=str(researcher.get('id', '')),
            additional_claims={'role': 'user'},
            expires_delta=timedelta(hours=3)
        )
        response = make_response(jsonify({'message': 'Login successful'}))
        set_access_cookies(response, token)
        
        logger.info(f"Successful login for: {username}")
        return response

    except Exception as e:
        logger.error(f"Authentication error: {str(e)}", exc_info=True)
        return jsonify({'message': 'Authentication failed'}), 500