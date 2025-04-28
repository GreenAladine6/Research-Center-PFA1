import os
import uuid
from datetime import datetime
from typing import Tuple, Optional, Dict, Any
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from Database.db import JSONDatabase

projects_bp = Blueprint('projects', __name__)
UPLOAD_FOLDER = os.path.join("fr/static", "images", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'svg'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def is_allowed_file(filename: str) -> bool:
    """Check if the uploaded file has a valid extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_project_data(data: Dict[str, Any], require_all_fields: bool = True) -> list:
    """Validate project data before insertion or update.

    Args:
        data: Dictionary containing project data.
        require_all_fields: Whether all fields are required (True for create, False for update).

    Returns:
        List of error messages; empty if valid.
    """
    required_fields = ['name_project', 'id_manager', 'state', 'budget', 'date_begin', 'date_end']
    errors = []
    
    if require_all_fields:
        for field in required_fields:
            if field not in data or not str(data[field]).strip():
                errors.append(f"Missing or empty required field: {field}")
    
    # Validate budget
    if 'budget' in data and data['budget']:
        try:
            budget = float(data['budget'])
            if budget < 0:
                errors.append("Budget must be non-negative")
        except ValueError:
            errors.append("Budget must be a valid number")
    
    # Validate dates
    for field in ['date_begin', 'date_end']:
        if field in data and data[field]:
            try:
                datetime.strptime(data[field], '%Y-%m-%d')
            except ValueError:
                errors.append(f"Invalid date format for {field}. Use YYYY-MM-DD")
    
    # Validate id_manager
    if 'id_manager' in data and data['id_manager']:
        try:
            id_manager = int(data['id_manager'])
            if id_manager <= 0:
                errors.append("Manager ID must be a positive integer")
        except ValueError:
            errors.append("Manager ID must be a valid integer")
    
    return errors

def handle_image_upload(
    request: Any, 
    old_image_path: Optional[str], 
    update_data: Dict[str, Any], 
    upload_folder: str = UPLOAD_FOLDER
) -> Tuple[bool, Optional[Dict[str, str]], Optional[int]]:
    """Handle image upload, preserve old image if no new image is provided.

    Args:
        request: Flask request object containing the file.
        old_image_path: Path to the old image (e.g., 'images/uploads/oldfile.jpg').
        update_data: Dictionary to store the new or existing image path.
        upload_folder: Folder where images are stored.

    Returns:
        Tuple: (success, response, status_code)
    """
    # If no new image, preserve old image path
    if 'image' not in request.files or request.files['image'].filename == '':
        if old_image_path:
            update_data["IMAGE"] = old_image_path
            current_app.logger.info(f"Preserved existing image: {old_image_path}")
        return True, None, None

    file = request.files['image']
    
    if not is_allowed_file(file.filename):
        return False, {"error": "Invalid file type. Allowed: jpg, jpeg, png, svg"}, 400

    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    if file_size > MAX_FILE_SIZE:
        return False, {"error": f"File too large. Maximum size: {MAX_FILE_SIZE // 1024 // 1024}MB"}, 400

    try:
        # Generate unique filename
        base_filename = secure_filename(file.filename)
        filename = f"{uuid.uuid4()}_{base_filename}"
        filepath = os.path.join(upload_folder, filename)
        image_path = f"images/uploads/{filename}"

        # Save new file
        os.makedirs(upload_folder, exist_ok=True)
        file.save(filepath)
        
        # Verify file was saved
        if not os.path.exists(filepath):
            current_app.logger.error(f"Failed to save image: {filepath}")
            return False, {"error": "Failed to save image"}, 500
        
        update_data["IMAGE"] = image_path
        current_app.logger.info(f"Saved new image: {filepath}")
        
        return True, None, None

    except Exception as e:
        current_app.logger.error(f"Error handling file upload: {str(e)}")
        return False, {"error": "Failed to process image"}, 500

def remove_old_image(old_image_path: Optional[str], new_image_path: Optional[str]):
    """Remove old image if it exists and is different from the new image."""
    if old_image_path and new_image_path and old_image_path != new_image_path:
        old_file_path = os.path.join("fr/static", old_image_path)
        if os.path.exists(old_file_path):
            try:
                os.remove(old_file_path)
                current_app.logger.info(f"Removed old image: {old_file_path}")
            except Exception as e:
                current_app.logger.warning(f"Could not remove old image: {str(e)}")

@projects_bp.post('/')
def create_project():
    """Create a new project.

    Returns:
        JSON response with project ID and status.
    """
    db = JSONDatabase()
    
    # Validate form data
    validation_errors = validate_project_data(request.form)
    if validation_errors:
        return jsonify({"error": "Validation failed", "details": validation_errors}), 400
    
    # Prepare project data
    update_data = {}
    for field in ['name_project', 'state', 'date_begin', 'date_end']:
        if field in request.form and request.form[field].strip():
            update_data[field.upper()] = request.form[field]
    if 'id_manager' in request.form and request.form['id_manager'].strip():
        update_data["ID_MANAGER"] = int(request.form['id_manager'])
    if 'budget' in request.form and request.form['budget'].strip():
        update_data["BUDGET"] = float(request.form['budget'])
    
    # Handle file upload
    success, response, status_code = handle_image_upload(request, None, update_data)
    if not success:
        return jsonify(response), status_code
    
    try:
        # Insert project
        project_id = db.insert_query("PROJECT", update_data)
        current_app.logger.info(f"Created project ID {project_id} with data: {update_data}")
        
        return jsonify({
            "success": True,
            "message": "Project created successfully",
            "project_id": project_id
        }), 201
    
    except Exception as e:
        current_app.logger.error(f"Error creating project: {str(e)}")
        return jsonify({"error": "Failed to create project", "details": str(e)}), 500

@projects_bp.get('/')
def get_projects():
    """Get all projects.

    Returns:
        JSON list of all projects.
    """
    try:
        db = JSONDatabase()
        projects = db.select_query("PROJECT")
        current_app.logger.info(f"Fetched {len(projects)} projects")
        return jsonify(projects), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching projects: {str(e)}")
        return jsonify({"error": "Failed to fetch projects", "details": str(e)}), 500

@projects_bp.get('/<int:project_id>')
def get_project(project_id: int):
    """Get a single project by ID.

    Args:
        project_id: The ID of the project to retrieve.

    Returns:
        JSON response with project data or error.
    """
    try:
        db = JSONDatabase()
        project = db.get_item("PROJECT", project_id)
        if project:
            current_app.logger.info(f"Fetched project ID {project_id}")
            return jsonify(project), 200
        current_app.logger.warning(f"Project ID {project_id} not found")
        return jsonify({"error": "Project not found"}), 404
    except Exception as e:
        current_app.logger.error(f"Error fetching project {project_id}: {str(e)}")
        return jsonify({"error": "Failed to fetch project", "details": str(e)}), 500

@projects_bp.put('/<int:project_id>')
def update_project(project_id: int):
    """Update an existing project.

    Args:
        project_id: The ID of the project to update.

    Request Form:
        - image: (optional) New project image.
        - name_project: (optional) Project name.
        - id_manager: (optional) Manager ID.
        - state: (optional) Project state.
        - budget: (optional) Project budget.
        - date_begin: (optional) Start date.
        - date_end: (optional) End date.

    Returns:
        JSON response with status.
    """
    db = JSONDatabase()
    
    # Check if project exists
    project = db.get_item("PROJECT", project_id)
    if not project:
        current_app.logger.warning(f"Project ID {project_id} not found")
        return jsonify({"error": "Project not found"}), 404
    
    old_image_path = project.get("IMAGE", "")
    
    # Validate input data
    validation_errors = validate_project_data(request.form, require_all_fields=False)
    if validation_errors:
        return jsonify({"error": "Validation failed", "details": validation_errors}), 400
    
    # Prepare update data by merging with existing project
    update_data = project.copy()  # Start with existing record
    for field in ['name_project', 'state', 'date_begin', 'date_end']:
        if field in request.form and request.form[field].strip():
            update_data[field.upper()] = request.form[field]
    if 'id_manager' in request.form and request.form['id_manager'].strip():
        update_data["ID_MANAGER"] = int(request.form['id_manager'])
    if 'budget' in request.form and request.form['budget'].strip():
        update_data["BUDGET"] = float(request.form['budget'])
    
    # Handle file upload
    success, response, status_code = handle_image_upload(request, old_image_path, update_data)
    if not success:
        return jsonify(response), status_code
    
    # Check if there are any changes
    if update_data == project:
        current_app.logger.info(f"No changes provided for project ID {project_id}")
        return jsonify({"success": True, "message": "No changes provided"}), 200
    
    try:
        # Update project
        if not db.update_query("PROJECT", project_id, update_data):
            current_app.logger.error(f"Failed to update project {project_id}: Record not found")
            return jsonify({"error": "Project not found"}), 404
        
        # Remove old image after successful database update
        remove_old_image(old_image_path, update_data.get("IMAGE"))
        current_app.logger.info(f"Updated project ID {project_id} with data: {update_data}")
        
        # Verify updated record
        updated_project = db.get_item("PROJECT", project_id)
        if not updated_project or updated_project["id"] != project_id:
            current_app.logger.error(f"Updated project ID {project_id} is corrupted or missing")
            return jsonify({"error": "Project update failed due to data corruption"}), 500
        
        return jsonify({
            "success": True,
            "message": "Project updated successfully",
            "project_id": project_id
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Error updating project {project_id}: {str(e)}")
        return jsonify({"error": "Failed to update project", "details": str(e)}), 500

@projects_bp.delete('/<int:project_id>')
def delete_project(project_id: int):
    """Delete a project.

    Args:
        project_id: The ID of the project to delete.

    Returns:
        JSON response with status.
    """
    db = JSONDatabase()
    
    try:
        project = db.get_item("PROJECT", project_id)
        if not project:
            current_app.logger.warning(f"Project ID {project_id} not found")
            return jsonify({"error": "Project not found"}), 404
        
        # Delete associated image
        if "IMAGE" in project:
            image_path = os.path.join("fr/static", project["IMAGE"])
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                    current_app.logger.info(f"Removed image: {image_path}")
                except Exception as e:
                    current_app.logger.warning(f"Could not remove project image: {str(e)}")
        
        # Delete project
        if not db.delete_query("PROJECT", project_id):
            current_app.logger.error(f"Failed to delete project {project_id}: Record not found")
            return jsonify({"error": "Project not found"}), 404
        
        current_app.logger.info(f"Deleted project ID {project_id}")
        return jsonify({
            "success": True,
            "message": "Project deleted successfully",
            "project_id": project_id
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Error deleting project {project_id}: {str(e)}")
        return jsonify({"error": "Failed to delete project", "details": str(e)}), 500

@projects_bp.get('/items')
def get_multiple_projects():
    """Get multiple projects by their IDs.

    Request JSON:
        List of project IDs to retrieve.

    Returns:
        JSON list of requested projects.
    """
    try:
        db = JSONDatabase()
        
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        project_ids = request.get_json()
        if not isinstance(project_ids, list):
            return jsonify({"error": "Expected array of project IDs"}), 400
        
        projects = []
        for project_id in project_ids:
            try:
                project = db.get_item("PROJECT", int(project_id))
                if project:
                    projects.append(project)
            except ValueError:
                current_app.logger.warning(f"Invalid project ID: {project_id}")
                continue
        
        current_app.logger.info(f"Fetched {len(projects)} projects by IDs")
        return jsonify(projects), 200
    
    except Exception as e:
        current_app.logger.error(f"Error fetching multiple projects: {str(e)}")
        return jsonify({"error": "Failed to fetch projects", "details": str(e)}), 500