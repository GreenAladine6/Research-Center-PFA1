from datetime import datetime
import os
from flask import Blueprint, request, jsonify, redirect, current_app
from werkzeug.utils import secure_filename
from Database.db import JSONDatabase

projects_bp = Blueprint('projects', __name__, url_prefix='/dashboard/projects')

# Define upload folder relative to blueprint
UPLOAD_FOLDER = os.path.join('dashboard', 'static', 'images', 'uploads')
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'svg'}

def is_allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None

@projects_bp.post('/')
def create_project():
    db = JSONDatabase()
    
    try:
        # Validate required fields
        required_fields = ['name_project', 'budget', 
                          'date_begin', 'date_end', 'etat']
        if not all(field in request.form for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        # Validate and parse input data
        try:
            budget = float(request.form['budget'])
            etat = int(request.form['etat'])
        except ValueError:
            return jsonify({"error": "Invalid numeric value"}), 400

        date_begin = validate_date(request.form['date_begin'])
        date_end = validate_date(request.form['date_end'])
        
        if not date_begin or not date_end:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
            
        if date_begin > date_end:
            return jsonify({"error": "End date must be after begin date"}), 400

        # Handle file upload
        filename = None
        file = request.files.get('image')
        if file and file.filename != '':
            if not is_allowed_file(file.filename):
                return jsonify({"error": "File type not allowed"}), 400
                
            filename = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
            filepath = os.path.join(current_app.root_path, UPLOAD_FOLDER, filename)
            
            # Ensure upload directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            file.save(filepath)
            filename = f"images/uploads/{filename}"

        # Insert into database
        project_data = {
            "ID_MANAGER": request.form.get('id_manager'),
            "NAME_PROJECT": request.form['name_project'],
            "BUDGET": budget,
            "DATE_BEGIN": request.form['date_begin'],
            "DATE_END": request.form['date_end'],
            "ETAT": etat,
            "IMAGE": filename
        }
        
        db.insert_query("project", project_data)
        return redirect('/dashboard/projects')
        
    except Exception as e:
        current_app.logger.error(f"Error creating project: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
@projects_bp.put('/<int:project_id>')
def update_project(project_id):
    db = JSONDatabase()
    
    try:
        # Get existing project
        project = db.get_item("project", project_id)
        if not project:
            return jsonify({"error": "Project not found"}), 404

        # Handle file upload if present
        filename = project.get('IMAGE')
        file = request.files.get('image')
        if file and file.filename != '' and is_allowed_file(file.filename):
            filename = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
            filepath = os.path.join(current_app.root_path, UPLOAD_FOLDER, filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            file.save(filepath)
            filename = f"images/uploads/{filename}"

        # Update project data
        update_data = {
            "ID_MANAGER": request.form.get('id_manager', project.get('ID_MANAGER')),
            "NAME_PROJECT": request.form.get('name', project['NAME_PROJECT']),
            "BUDGET": float(request.form.get('budget', project['BUDGET'])),
            "DATE_BEGIN": request.form.get('date_begin', project['DATE_BEGIN']),
            "DATE_END": request.form.get('date_end', project['DATE_END']),
            "ETAT": int(request.form.get('etat', project['ETAT'])),
            "IMAGE": filename
        }

        db.update_query("project", project_id, update_data)
        return jsonify({"success": True}), 200
        
    except ValueError as e:
        return jsonify({"error": f"Invalid data format: {str(e)}"}), 400
    except Exception as e:
        current_app.logger.error(f"Error updating project {project_id}: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
@projects_bp.get('/')
def get_projects():
    db = JSONDatabase()
    try:
        projects = db.select_query("project")
        return jsonify(projects), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching projects: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@projects_bp.get('/<int:project_id>')
def get_project(project_id):
    db = JSONDatabase()
    try:
        project = db.get_item("project", project_id)
        if not project:
            return jsonify({"error": "Project not found"}), 404
        return jsonify(project), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching project {project_id}: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@projects_bp.delete('/<int:project_id>')
def delete_project(project_id):
    db = JSONDatabase()
    try:
        if not db.get_item("project", project_id):
            return jsonify({"error": "Project not found"}), 404
    except Exception as e:
        current_app.logger.error(f"Error deleting project {project_id}: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500