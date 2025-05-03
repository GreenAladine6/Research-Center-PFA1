from datetime import timedelta
import os
import bcrypt
from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import create_access_token, set_access_cookies
from Database.db import JSONDatabase

auth_bp = Blueprint('auth', __name__)

# Environment variables
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')  # Stored in plaintext
db = JSONDatabase()

def ensure_string(value, default=''):
    """Ensure the value is a string, casting if necessary"""
    try:
        return str(value) if value is not None else default
    except:
        return default

@auth_bp.post('/login')
def login():
    data = request.json
    if not data:
        return jsonify({'message': 'Invalid request'}), 400

    # Get and validate credentials
    username = ensure_string(data.get('username'))
    password = ensure_string(data.get('password'))
    
    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    try:
        # Admin login (plaintext comparison)
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

        # Researcher login (hashed passwords)
        researchers = db.select_query("RESEARCHER")
        for researcher in researchers:
            # Cast all fields to strings
            researcher_email = ensure_string(researcher.get('EMAIL', '')).lower().strip()
            researcher_password = ensure_string(researcher.get('PASSWORD', ''))
            researcher_id = ensure_string(researcher.get('id', ''))

            if researcher_email == username.lower().strip():
                # Verify hashed password
                if bcrypt.checkpw(password.encode('utf-8'), researcher_password.encode('utf-8')):
                    token = create_access_token(
                        identity=researcher_id,
                        additional_claims={'role': 'user'},
                        expires_delta=timedelta(hours=3)
                    )
                    response = make_response(jsonify({'message': 'Researcher login successful'}))
                    set_access_cookies(response, token)
                    return response

        return jsonify({'message': 'Invalid credentials'}), 401

    except (bcrypt.exceptions.InvalidHash, ValueError) as e:
        return jsonify({'message': 'Authentication error'}), 500