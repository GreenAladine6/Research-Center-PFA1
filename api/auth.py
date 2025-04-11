from datetime import timedelta
import os
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies

# Create Blueprint for authentication
auth_bp = Blueprint('auth', __name__)

# Get credentials from environment variables
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

@auth_bp.post('/login')
def login():
    data = request.json
    if not data:
        return jsonify({'message': 'Invalid request'}), 400

    username = data.get('username')
    password = data.get('password')

    # Check if credentials match
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        # Create JWT token that expires in 3 hours
        token = create_access_token(identity=username, expires_delta=timedelta(hours=3))

        # Set the token in an HTTP-only cookie
        response = make_response(jsonify({'message': 'Login successful'}))
        set_access_cookies(response, token)

        return response

    return jsonify({'message': 'Login failed'}), 401
@auth_bp.post('/logout')
def logout():
    # Create a response object
    response = make_response(jsonify({'message': 'Logout successful'}))

    # Unset the JWT cookie
    unset_jwt_cookies(response)

    return response