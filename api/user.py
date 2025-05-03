import os
import uuid
import bcrypt
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from Database.db import JSONDatabase

user_bp = Blueprint('user', __name__)
UPLOAD_FOLDER = os.path.join("static", "images", "uploads", "staff")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'svg'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def is_allowed_file(filename: str) -> bool:
    """Check if the uploaded file has a valid extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_user_data(data: dict, require_all_fields: bool = False) -> list:
    """Validate user data for update."""
    errors = []
    
    # Validate email
    if 'email' in data and data['email']:
        import re
        email_pattern = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')
        if not email_pattern.match(data['email']):
            errors.append("Invalid email format")
    
    # Validate password
    if 'password' in data and data['password']:
        if len(data['password']) < 8:
            errors.append("Password must be at least 8 characters long")
        if 'confirm_password' not in data or data['password'] != data['confirm_password']:
            errors.append("Passwords do not match")
    
    if require_all_fields and not data.get('email') and not data.get('password') and 'image' not in request.files:
        errors.append("At least one field (email, password, or image) must be provided")
    
    return errors

def handle_image_upload(
    request, 
    old_image_path: str | None, 
    update_data: dict, 
    upload_folder: str = UPLOAD_FOLDER
) -> tuple[bool, dict | None, int | None]:
    """Handle profile picture upload, preserve old image if no new image is provided."""
    if 'image' not in request.files or request.files['image'].filename == '':
        if old_image_path:
            update_data["IMAGE"] = old_image_path
            current_app.logger.info(f"Preserved existing image: {old_image_path}")
        return True, None, None

    file = request.files['image']
    
    if not is_allowed_file(file.filename):
        return False, {"error": "Invalid file type. Allowed: jpg, jpeg, png, svg"}, 400

    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    if file_size > MAX_FILE_SIZE:
        return False, {"error": f"File too large. Maximum size: {MAX_FILE_SIZE // 1024 // 1024}MB"}, 400

    try:
        base_filename = secure_filename(file.filename)
        filename = f"{uuid.uuid4()}_{base_filename}"
        filepath = os.path.join(upload_folder, filename)
        image_path = f"images/uploads/staff/{filename}"

        os.makedirs(upload_folder, exist_ok=True)
        file.save(filepath)
        
        if not os.path.exists(filepath):
            current_app.logger.error(f"Failed to save image: {filepath}")
            return False, {"error": "Failed to save image"}, 500
        
        update_data["IMAGE"] = image_path
        current_app.logger.info(f"Saved new image: {filepath}")
        
        return True, None, None

    except Exception as e:
        current_app.logger.error(f"Error handling file upload: {str(e)}")
        return False, {"error": "Failed to process image"}, 500

def remove_old_image(old_image_path: str | None, new_image_path: str | None):
    """Remove old image if it exists and is different from the new image."""
    if old_image_path and new_image_path and old_image_path != new_image_path:
        old_file_path = os.path.join("static", old_image_path)
        if os.path.exists(old_file_path):
            try:
                os.remove(old_file_path)
                current_app.logger.info(f"Removed old image: {old_file_path}")
            except Exception as e:
                current_app.logger.warning(f"Could not remove old image: {str(e)}")

@user_bp.put('/<int:user_id>')
def update_profile(user_id: int):
    """Update an existing user."""
    db = JSONDatabase()
    
    user = db.get_item("USER", user_id)
    if not user:
        current_app.logger.warning(f"User ID {user_id} not found")
        return jsonify({"error": "User not found"}), 404
    
    old_image_path = user.get("IMAGE", "")
    
    validation_errors = validate_user_data(request.form, require_all_fields=False)
    if validation_errors:
        return jsonify({"error": "Validation failed", "details": validation_errors}), 400
    
    update_data = user.copy()
    for field in ['full_name', 'bio']:
        if field in request.form and request.form[field].strip():
            update_data[field.upper()] = request.form[field]
    
    if 'Grade' in request.form:
        grade_value = request.form['Grade']
        if grade_value == 'No grade':
            update_data['GRADE'] = None
        else:
            try:
                update_data['GRADE'] = int(grade_value)
            except ValueError:
                return jsonify({"error": "Invalid grade ID"}), 400
    
    success, response, status_code = handle_image_upload(request, old_image_path, update_data)
    if not success:
        return jsonify(response), status_code
    
    if update_data == user:
        current_app.logger.info(f"No changes provided for user ID {user_id}")
        return jsonify({"success": True, "message": "No changes provided"}), 200
    
    try:
        if not db.update_query("USER", user_id, update_data):
            current_app.logger.error(f"Failed to update user {user_id}: Record not found")
            return jsonify({"error": "User not found"}), 404
        
        remove_old_image(old_image_path, update_data.get("IMAGE"))
        current_app.logger.info(f"Updated user ID {user_id} with data: {update_data}")
        
        updated_user = db.get_item("USER", user_id)
        if not updated_user or updated_user["id"] != user_id:
            current_app.logger.error(f"Updated user ID {user_id} is corrupted or missing")
            return jsonify({"error": "User update failed due to data corruption"}), 500
        
        return jsonify({
            "success": True,
            "message": "User updated successfully",
            "user_id": user_id
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Error updating user {user_id}: {str(e)}")
        return jsonify({"error": "Failed to update user", "details": str(e)}), 500
@user_bp.patch('/<int:user_id>/quit')
def quit_profile(user_id: int):
    """Deactivate a user profile."""
    db = JSONDatabase()
    user = db.get_item("USER", user_id)
    if not user:
        current_app.logger.warning(f"User ID {user_id} not found for quit")
        return jsonify({"error": "User not found"}), 404
    try:
        update_data = user.copy()
        update_data['ACTIVE'] = False  # Assuming 'ACTIVE' field controls active status
        if not db.update_query("USER", user_id, update_data):
            current_app.logger.error(f"Failed to deactivate user {user_id}")
            return jsonify({"error": "Failed to deactivate user"}), 500
        current_app.logger.info(f"User ID {user_id} deactivated successfully")
        return jsonify({"success": True, "message": "User deactivated successfully"}), 200
    except Exception as e:
        current_app.logger.error(f"Error deactivating user {user_id}: {str(e)}")
        return jsonify({"error": "Failed to deactivate user", "details": str(e)}), 500