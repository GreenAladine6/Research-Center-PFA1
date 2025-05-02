import os
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from Database.db import JSONDatabase

publications_bp = Blueprint('publications', __name__)
UPLOAD_FOLDER = os.path.join("static", "images", "uploads", "publications")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'svg'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def is_allowed_file(filename: str) -> bool:
    """Check if the uploaded file has a valid extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_publication_data(data: dict, require_all_fields: bool = True) -> list:
    """Validate publication data before insertion or update."""
    required_fields = ['title', 'id_researcher', 'description', 'date']
    errors = []
    
    if require_all_fields:
        for field in required_fields:
            if field not in data or not str(data[field]).strip():
                errors.append(f"Missing or empty required field: {field}")
    
    # Validate date
    if 'date' in data and data['date']:
        try:
            datetime.strptime(data['date'], '%Y-%m-%d')
        except ValueError:
            errors.append("Invalid date format for date. Use YYYY-MM-DD")
    
    # Validate id_researcher
    if 'id_researcher' in data and data['id_researcher']:
        try:
            id_researcher = int(data['id_researcher'])
            if id_researcher <= 0:
                errors.append("Researcher ID must be a positive integer")
            else:
                db = JSONDatabase()
                researcher = db.get_item("RESEARCHER", id_researcher)
                if not researcher:
                    errors.append("Invalid Researcher ID: Researcher does not exist")
        except ValueError:
            errors.append("Researcher ID must be a valid integer")
    
    # Validate link if provided
    if 'link' in data and data['link']:
        import re
        url_pattern = re.compile(
            r'^(https?:\/\/)?'  # protocol
            r'([\da-z\.-]+)\.([a-z\.]{2,6})'  # domain
            r'([\/\w \.-]*)*\/?$'  # path
        )
        if not url_pattern.match(data['link']):
            errors.append("Invalid URL format for link")
    
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
        image_path = f"images/uploads/publications/{filename}"

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

@publications_bp.post('/')
def create_publication():
    """Create a new publication."""
    db = JSONDatabase()
    
    validation_errors = validate_publication_data(request.form)
    if validation_errors:
        return jsonify({"error": "Validation failed", "details": validation_errors}), 400
    
    update_data = {}
    for field in ['title', 'description', 'link', 'date']:
        if field in request.form and request.form[field].strip():
            update_data[field.upper()] = request.form[field]
    if 'id_researcher' in request.form and request.form['id_researcher'].strip():
        update_data["ID_RESEARCHER"] = int(request.form['id_researcher'])
    
    success, response, status_code = handle_image_upload(request, None, update_data)
    if not success:
        return jsonify(response), status_code
    
    try:
        publication_id = db.insert_query("PUBLICATION", update_data)
        current_app.logger.info(f"Created publication ID {publication_id} with data: {update_data}")
        
        return jsonify({
            "success": True,
            "message": "Publication created successfully",
            "publication_id": publication_id
        }), 201
    
    except Exception as e:
        current_app.logger.error(f"Error creating publication: {str(e)}")
        return jsonify({"error": "Failed to create publication", "details": str(e)}), 500

@publications_bp.get('/')
def get_publications():
    """Get all publications."""
    try:
        db = JSONDatabase()
        publications = db.select_query("PUBLICATION")
        current_app.logger.info(f"Fetched {len(publications)} publications")
        return jsonify(publications), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching publications: {str(e)}")
        return jsonify({"error": "Failed to fetch publications", "details": str(e)}), 500

@publications_bp.get('/<int:publication_id>')
def get_publication(publication_id: int):
    """Get a single publication by ID."""
    try:
        db = JSONDatabase()
        publication = db.get_item("PUBLICATION", publication_id)
        if publication:
            current_app.logger.info(f"Fetched publication ID {publication_id}")
            return jsonify(publication), 200
        current_app.logger.warning(f"Publication ID {publication_id} not found")
        return jsonify({"error": "Publication not found"}), 404
    except Exception as e:
        current_app.logger.error(f"Error fetching publication {publication_id}: {str(e)}")
        return jsonify({"error": "Failed to fetch publication", "details": str(e)}), 500

@publications_bp.put('/<int:publication_id>')
def update_publication(publication_id: int):
    """Update an existing publication."""
    db = JSONDatabase()
    
    publication = db.get_item("PUBLICATION", publication_id)
    if not publication:
        current_app.logger.warning(f"Publication ID {publication_id} not found")
        return jsonify({"error": "Publication not found"}), 404
    
    old_image_path = publication.get("IMAGE", "")
    
    validation_errors = validate_publication_data(request.form, require_all_fields=False)
    if validation_errors:
        return jsonify({"error": "Validation failed", "details": validation_errors}), 400
    
    update_data = publication.copy()
    for field in ['title', 'description', 'link', 'date']:
        if field in request.form and request.form[field].strip():
            update_data[field.upper()] = request.form[field]
    if 'id_researcher' in request.form and request.form['id_researcher'].strip():
        update_data["ID_RESEARCHER"] = int(request.form['id_researcher'])
    
    success, response, status_code = handle_image_upload(request, old_image_path, update_data)
    if not success:
        return jsonify(response), status_code
    
    if update_data == publication:
        current_app.logger.info(f"No changes provided for publication ID {publication_id}")
        return jsonify({"success": True, "message": "No changes provided"}), 200
    
    try:
        if not db.update_query("PUBLICATION", publication_id, update_data):
            current_app.logger.error(f"Failed to update publication {publication_id}: Record not found")
            return jsonify({"error": "Publication not found"}), 404
        
        remove_old_image(old_image_path, update_data.get("IMAGE"))
        current_app.logger.info(f"Updated publication ID {publication_id} with data: {update_data}")
        
        updated_publication = db.get_item("PUBLICATION", publication_id)
        if not updated_publication or updated_publication["id"] != publication_id:
            current_app.logger.error(f"Updated publication ID {publication_id} is corrupted or missing")
            return jsonify({"error": "Publication update failed due to data corruption"}), 500
        
        return jsonify({
            "success": True,
            "message": "Publication updated successfully",
            "publication_id": publication_id
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Error updating publication {publication_id}: {str(e)}")
        return jsonify({"error": "Failed to update publication", "details": str(e)}), 500

@publications_bp.delete('/<int:publication_id>')
def delete_publication(publication_id: int):
    """Delete a publication."""
    db = JSONDatabase()
    
    try:
        publication = db.get_item("PUBLICATION", publication_id)
        if not publication:
            current_app.logger.warning(f"Publication ID {publication_id} not found")
            return jsonify({"error": "Publication not found"}), 404
        
        if "IMAGE" in publication:
            image_path = os.path.join("static", publication["IMAGE"])
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                    current_app.logger.info(f"Removed image: {image_path}")
                except Exception as e:
                    current_app.logger.warning(f"Could not remove publication image: {str(e)}")
        
        if not db.delete_query("PUBLICATION", publication_id):
            current_app.logger.error(f"Failed to delete publication {publication_id}: Record not found")
            return jsonify({"error": "Publication not found"}), 404
        
        current_app.logger.info(f"Deleted publication ID {publication_id}")
        return jsonify({
            "success": True,
            "message": "Publication deleted successfully",
            "publication_id": publication_id
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Error deleting publication {publication_id}: {str(e)}")
        return jsonify({"error": "Failed to delete publication", "details": str(e)}), 500

@publications_bp.get('/items')
def get_multiple_publications():
    """Get multiple publications by their IDs."""
    try:
        db = JSONDatabase()
        
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        publication_ids = request.get_json()
        if not isinstance(publication_ids, list):
            return jsonify({"error": "Expected array of publication IDs"}), 400
        
        publications = []
        for publication_id in publication_ids:
            try:
                publication = db.get_item("PUBLICATION", int(publication_id))
                if publication:
                    publications.append(publication)
            except ValueError:
                current_app.logger.warning(f"Invalid publication ID: {publication_id}")
                continue
        
        current_app.logger.info(f"Fetched {len(publications)} publications by IDs")
        return jsonify(publications), 200
    
    except Exception as e:
        current_app.logger.error(f"Error fetching multiple publications: {str(e)}")
        return jsonify({"error": "Failed to fetch publications", "details": str(e)}), 500