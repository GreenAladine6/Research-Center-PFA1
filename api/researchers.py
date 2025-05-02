import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from Database.db import JSONDatabase

researchers_bp = Blueprint('researchers', __name__)
UPLOAD_FOLDER = os.path.join("static", "images", "uploads", "staff")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'svg'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def is_allowed_file(filename: str) -> bool:
    """Check if the uploaded file has a valid extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_researcher_data(data: dict, require_all_fields: bool = True) -> list:
    """Validate researcher data before insertion or update."""
    required_fields = ['full_name', 'Grade']
    errors = []
    
    if require_all_fields:
        for field in required_fields:
            if field not in data or not str(data[field]).strip():
                errors.append(f"Missing or empty required field: {field}")
    
    # Validate Grade
    if 'Grade' in data:
        grade_value = data['Grade']
        if grade_value != 'No grade':
            try:
                int(grade_value)  # Ensure it's a valid integer
            except ValueError:
                errors.append("Invalid grade ID")
    
    return errors

def handle_image_upload(
    request, 
    old_image_path: str | None, 
    update_data: dict, 
    upload_folder: str = UPLOAD_FOLDER
) -> tuple[bool, dict | None, int | None]:
    """Handle image upload, preserve old image if no new image is provided."""
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

@researchers_bp.post('/')
def create_researcher():
    """Create a new researcher."""
    db = JSONDatabase()
    
    validation_errors = validate_researcher_data(request.form)
    if validation_errors:
        return jsonify({"error": "Validation failed", "details": validation_errors}), 400
    
    update_data = {}
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
    
    success, response, status_code = handle_image_upload(request, None, update_data)
    if not success:
        return jsonify(response), status_code
    
    try:
        researcher_id = db.insert_query("RESEARCHER", update_data)
        current_app.logger.info(f"Created researcher ID {researcher_id} with data: {update_data}")
        
        return jsonify({
            "success": True,
            "message": "Researcher created successfully",
            "researcher_id": researcher_id
        }), 201
    
    except Exception as e:
        current_app.logger.error(f"Error creating researcher: {str(e)}")
        return jsonify({"error": "Failed to create researcher", "details": str(e)}), 500

@researchers_bp.get('/')
def get_researchers():
    """Get all researchers."""
    try:
        db = JSONDatabase()
        researchers = db.select_query("RESEARCHER")
        current_app.logger.info(f"Fetched {len(researchers)} researchers")
        return jsonify(researchers), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching researchers: {str(e)}")
        return jsonify({"error": "Failed to fetch researchers", "details": str(e)}), 500

@researchers_bp.get('/<int:researcher_id>')
def get_researcher(researcher_id: int):
    """Get a single researcher by ID."""
    try:
        db = JSONDatabase()
        researcher = db.get_item("RESEARCHER", researcher_id)
        if researcher:
            current_app.logger.info(f"Fetched researcher ID {researcher_id}")
            return jsonify(researcher), 200
        current_app.logger.warning(f"Researcher ID {researcher_id} not found")
        return jsonify({"error": "Researcher not found"}), 404
    except Exception as e:
        current_app.logger.error(f"Error fetching researcher {researcher_id}: {str(e)}")
        return jsonify({"error": "Failed to fetch researcher", "details": str(e)}), 500

@researchers_bp.put('/<int:researcher_id>')
def update_researcher(researcher_id: int):
    """Update an existing researcher."""
    db = JSONDatabase()
    
    researcher = db.get_item("RESEARCHER", researcher_id)
    if not researcher:
        current_app.logger.warning(f"Researcher ID {researcher_id} not found")
        return jsonify({"error": "Researcher not found"}), 404
    
    old_image_path = researcher.get("IMAGE", "")
    
    validation_errors = validate_researcher_data(request.form, require_all_fields=False)
    if validation_errors:
        return jsonify({"error": "Validation failed", "details": validation_errors}), 400
    
    update_data = researcher.copy()
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
    
    if update_data == researcher:
        current_app.logger.info(f"No changes provided for researcher ID {researcher_id}")
        return jsonify({"success": True, "message": "No changes provided"}), 200
    
    try:
        if not db.update_query("RESEARCHER", researcher_id, update_data):
            current_app.logger.error(f"Failed to update researcher {researcher_id}: Record not found")
            return jsonify({"error": "Researcher not found"}), 404
        
        remove_old_image(old_image_path, update_data.get("IMAGE"))
        current_app.logger.info(f"Updated researcher ID {researcher_id} with data: {update_data}")
        
        updated_researcher = db.get_item("RESEARCHER", researcher_id)
        if not updated_researcher or updated_researcher["id"] != researcher_id:
            current_app.logger.error(f"Updated researcher ID {researcher_id} is corrupted or missing")
            return jsonify({"error": "Researcher update failed due to data corruption"}), 500
        
        return jsonify({
            "success": True,
            "message": "Researcher updated successfully",
            "researcher_id": researcher_id
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Error updating researcher {researcher_id}: {str(e)}")
        return jsonify({"error": "Failed to update researcher", "details": str(e)}), 500

@researchers_bp.delete('/<int:researcher_id>')
def delete_researcher(researcher_id: int):
    """Delete a researcher."""
    db = JSONDatabase()
    
    try:
        researcher = db.get_item("RESEARCHER", researcher_id)
        if not researcher:
            current_app.logger.warning(f"Researcher ID {researcher_id} not found")
            return jsonify({"error": "Researcher not found"}), 404
        
        if "IMAGE" in researcher:
            image_path = os.path.join("static", researcher["IMAGE"])
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                    current_app.logger.info(f"Removed image: {image_path}")
                except Exception as e:
                    current_app.logger.warning(f"Could not remove researcher image: {str(e)}")
        
        if not db.delete_query("RESEARCHER", researcher_id):
            current_app.logger.error(f"Failed to delete researcher {researcher_id}: Record not found")
            return jsonify({"error": "Researcher not found"}), 404
        
        current_app.logger.info(f"Deleted researcher ID {researcher_id}")
        return jsonify({
            "success": True,
            "message": "Researcher deleted successfully",
            "researcher_id": researcher_id
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Error deleting researcher {researcher_id}: {str(e)}")
        return jsonify({"error": "Failed to delete researcher", "details": str(e)}), 500

@researchers_bp.get('/items')
def get_multiple_researchers():
    """Get multiple researchers by their IDs."""
    try:
        db = JSONDatabase()
        
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        researcher_ids = request.get_json()
        if not isinstance(researcher_ids, list):
            return jsonify({"error": "Expected array of researcher IDs"}), 400
        
        researchers = []
        for researcher_id in researcher_ids:
            try:
                researcher = db.get_item("RESEARCHER", int(researcher_id))
                if researcher:
                    researchers.append(researcher)
            except ValueError:
                current_app.logger.warning(f"Invalid researcher ID: {researcher_id}")
                continue
        
        current_app.logger.info(f"Fetched {len(researchers)} researchers by IDs")
        return jsonify(researchers), 200
    
    except Exception as e:
        current_app.logger.error(f"Error fetching multiple researchers: {str(e)}")
        return jsonify({"error": "Failed to fetch researchers", "details": str(e)}), 500