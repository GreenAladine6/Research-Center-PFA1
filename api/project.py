from datetime import datetime
import os
from flask import Blueprint, request, jsonify, redirect, current_app
from werkzeug.utils import secure_filename
from Database.db import JSONDatabase

projects_bp = Blueprint('projects', __name__)
UPLOAD_FOLDER = os.path.join("static", "images", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'svg'}

def is_allowed_file(filename):
    """Check if the uploaded file has a valid extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_project_data(data, require_all_fields=True):
    """Validate project data before insertion or update."""
    required_fields = ['name_project', 'id_manager', 'state', 'budget', 'date_begin', 'date_end']
    errors = []
    
    if require_all_fields:
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
    
    # Validate budget is numeric if provided
    if 'budget' in data:
        try:
            float(data['budget'])
        except ValueError:
            errors.append("Budget must be a valid number")
    
    # Validate dates if provided
    date_fields = ['date_begin', 'date_end']
    for field in date_fields:
        if field in data:
            try:
                datetime.strptime(data[field], '%Y-%m-%d')
            except ValueError:
                errors.append(f"Invalid date format for {field}. Use YYYY-MM-DD")
    
    return errors

@projects_bp.post('/')
def create_project():
    """Create a new project."""
    db = JSONDatabase()
    
    # Check for required fields
    validation_errors = validate_project_data(request.form)
    if validation_errors:
        return jsonify({"error": "Validation failed", "details": validation_errors}), 400
    
    # Handle file upload
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if not is_allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400
    
    try:
        # Save the file with timestamp prefix
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = secure_filename(f"{timestamp}_{file.filename}")
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Prepare project data
        project_data = {
            "ID_MANAGER": int(request.form['id_manager']),
            "NAME_PROJECT": request.form['name_project'],
            "BUDGET": float(request.form['budget']),
            "DATE_BEGIN": request.form['date_begin'],
            "DATE_END": request.form['date_end'],
            "STATUS": request.form['state'],
            "IMAGE": f"images/uploads/{filename}"  # relative path
        }
        
        # Insert project
        project_id = db.insert_query("PROJECT", project_data)
        
        return jsonify({
            "success": True,
            "message": "Project created successfully",
            "project_id": project_id
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error creating project: {str(e)}")
        return jsonify({"error": "Failed to create project"}), 500

@projects_bp.get('/')
def get_projects():
    projects = []
    try:
        db = JSONDatabase()
        projects = db.select_query("PROJECT")
        return jsonify(projects), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching projects: {str(e)}")
        return jsonify({"error": "Failed to fetch projects"}), 500

@projects_bp.get('/<int:project_id>')
def get_project(project_id):
    items = []
    db = JSONDatabase()
    items = db.select_query("PROJECT", {"ID_PROJECT": project_id})
    if project_id:
        return db.get_item("PROJECT", int(project_id))
    return items

@projects_bp.put('/<int:project_id>')
def update_project(project_id):
    """Update an existing project.
    
    Args:
        project_id: The ID of the project to update
    
    Request Form:
    - image: (optional) New project image
    - name_project: (optional) Project name
    - id_manager: (optional) Manager ID
    - state: (optional) Project state
    - budget: (optional) Project budget
    - date_begin: (optional) Start date
    - date_end: (optional) End date
    
    Returns:
    - 200: Project updated successfully
    - 400: Invalid request data
    - 404: Project not found
    - 500: Server error
    """
    db = JSONDatabase()
    
    # Check if project exists
    projects = db.select_query("PROJECT", {"ID_PROJECT": project_id})
    if not projects:
        return jsonify({"error": "Project not found"}), 404
    
    project = projects[0]
    old_image_path = project.get("IMAGE", "")
    
    # Validate input data
    validation_errors = validate_project_data(request.form, require_all_fields=False)
    if validation_errors:
        return jsonify({"error": "Validation failed", "details": validation_errors}), 400
    
    # Prepare update data
    update_data = {}
    if 'name_project' in request.form:
        update_data["NAME_PROJECT"] = request.form['name_project']
    if 'id_manager' in request.form:
        update_data["ID_MANAGER"] = int(request.form['id_manager'])
    if 'state' in request.form:
        update_data["STATUS"] = request.form['state']
    if 'budget' in request.form:
        update_data["BUDGET"] = float(request.form['budget'])
    if 'date_begin' in request.form:
        update_data["DATE_BEGIN"] = request.form['date_begin']
    if 'date_end' in request.form:
        update_data["DATE_END"] = request.form['date_end']
    
    # Handle file upload if present
    if 'image' in request.files and request.files['image'].filename != '':
        file = request.files['image']
        
        if not is_allowed_file(file.filename):
            return jsonify({"error": "Invalid file type"}), 400
            
        try:
            # Save new file
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = secure_filename(f"{timestamp}_{file.filename}")
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            # Update image path
            update_data["IMAGE"] = f"images/uploads/{filename}"
            
            # Remove old image if it exists
            if old_image_path:
                old_file_path = os.path.join("static", old_image_path)
                if os.path.exists(old_file_path):
                    try:
                        os.remove(old_file_path)
                    except Exception as e:
                        current_app.logger.warning(f"Could not remove old image: {str(e)}")
        except Exception as e:
            current_app.logger.error(f"Error handling file upload: {str(e)}")
            return jsonify({"error": "Failed to process image"}), 500
    
    try:
        # Update project
        db.update_query("PROJECT", project_id, update_data)
        
        return jsonify({
            "success": True,
            "message": "Project updated successfully",
            "project_id": project_id
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error updating project {project_id}: {str(e)}")
        return jsonify({"error": "Failed to update project"}), 500

@projects_bp.delete('/<int:project_id>')
def delete_project(project_id):
    """Delete a project.
    
    Args:
        project_id: The ID of the project to delete
    
    Returns:
    - 200: Project deleted successfully
    - 404: Project not found
    - 500: Server error
    """
    db = JSONDatabase()
    
    try:
        # Check if project exists
        projects = db.select_query("PROJECT", {"ID_PROJECT": project_id})
        if not projects:
            return jsonify({"error": "Project not found"}), 404
        
        project = projects[0]
        
        # Delete associated image if it exists
        if "IMAGE" in project:
            image_path = os.path.join("static", project["IMAGE"])
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                except Exception as e:
                    current_app.logger.warning(f"Could not remove project image: {str(e)}")
        
        # Delete project from database
        db.delete_query("PROJECT", project_id)
        
        return jsonify({
            "success": True,
            "message": "Project deleted successfully",
            "project_id": project_id
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error deleting project {project_id}: {str(e)}")
        return jsonify({"error": "Failed to delete project"}), 500

@projects_bp.get('/items')
def get_multiple_projects():
    """Get multiple projects by their IDs.
    
    Request JSON:
    - List of project IDs to retrieve
    
    Returns:
    - 200: List of requested projects
    - 400: Invalid request
    - 500: Server error
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
                project = db.select_query("PROJECT", {"ID_PROJECT": int(project_id)})
                if project:
                    projects.append(project[0])
            except ValueError:
                continue  # Skip invalid IDs
        
        return jsonify(projects), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching multiple projects: {str(e)}")
        return jsonify({"error": "Failed to fetch projects"}), 500