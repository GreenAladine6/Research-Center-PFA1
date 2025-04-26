
import os
import uuid
from datetime import datetime
from typing import Tuple, Optional, Dict, Any
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from Database.db import JSONDatabase

events_bp = Blueprint('events', __name__)
UPLOAD_FOLDER = os.path.join("static", "images", "uploads","events")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'svg'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def is_allowed_file(filename: str) -> bool:
    """Check if the uploaded file has a valid extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_event_data(data: Dict[str, Any], require_all_fields: bool = True) -> list:
    """Validate event data before insertion or update.

    Args:
        data: Dictionary containing event data.
        require_all_fields: Whether all fields are required (True for create, False for update).

    Returns:
        List of error messages; empty if valid.
    """
    required_fields = ['name_event','type_event' ,'id_organisor', 'date_begin', 'hour', 'date_end', 'place']
    errors = []
    
    if require_all_fields:
        for field in required_fields:
            if field not in data or not str(data[field]).strip():
                errors.append(f"Missing or empty required field: {field}")
    
    # Validate place
    if 'hour' in data and data['hour']:
        try:
                datetime.strptime(data['hour'], '%H:%M')
        except ValueError:
            errors.append("Invalid time format for hour. Use HH:MM")
    
    # Validate dates
    for field in ['date_begin', 'date_end']:
        if field in data and data[field]:
            try:
                datetime.strptime(data[field], '%Y-%m-%d')
            except ValueError:
                errors.append(f"Invalid date format for {field}. Use YYYY-MM-DD")
    
    # Validate id_organisor
    if 'id_organisor' in data and data['id_organisor']:
        try:
            id_organisor = int(data['id_organisor'])
            if id_organisor <= 0:
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
        image_path = f"images/uploads/events/{filename}"

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
        old_file_path = os.path.join("static", old_image_path)
        if os.path.exists(old_file_path):
            try:
                os.remove(old_file_path)
                current_app.logger.info(f"Removed old image: {old_file_path}")
            except Exception as e:
                current_app.logger.warning(f"Could not remove old image: {str(e)}")

@events_bp.post('/')
def create_event():
    """Create a new event.

    Returns:
        JSON response with event ID and status.
    """
    db = JSONDatabase()
    
    # Validate form data
    validation_errors = validate_event_data(request.form)
    if validation_errors:
        return jsonify({"error": "Validation failed", "details": validation_errors}), 400
    
    # Prepare event data
    update_data = {}
    for field in ['name_event', 'hour', 'date_begin', 'date_end','type_event']:
        if field in request.form and request.form[field].strip():
            update_data[field.upper()] = request.form[field]
    if 'type_event' in request.form and request.form['type_event'].strip():
        update_data["TYPE_EVENT"] = request.form['type_event']
    if 'id_organisor' in request.form and request.form['id_organisor'].strip():
        update_data["ID_ORGANISOR"] = int(request.form['id_organisor'])
    if 'place' in request.form and request.form['place'].strip():
        update_data["PLACE"] = float(request.form['place'])
    
    # Handle file upload
    success, response, status_code = handle_image_upload(request, None, update_data)
    if not success:
        return jsonify(response), status_code
    
    try:
        # Insert event
        event_id = db.insert_query("EVENT", update_data)
        current_app.logger.info(f"Created event ID {event_id} with data: {update_data}")
        
        return jsonify({
            "success": True,
            "message": "Event created successfully",
            "event_id": event_id
        }), 201
    
    except Exception as e:
        current_app.logger.error(f"Error creating event: {str(e)}")
        return jsonify({"error": "Failed to create event", "details": str(e)}), 500

@events_bp.get('/')
def get_events():
    """Get all events.

    Returns:
        JSON list of all events.
    """
    try:
        db = JSONDatabase()
        events = db.select_query("EVENT")
        current_app.logger.info(f"Fetched {len(events)} events")
        return jsonify(events), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching events: {str(e)}")
        return jsonify({"error": "Failed to fetch events", "details": str(e)}), 500

@events_bp.get('/<int:event_id>')
def get_event(event_id: int):
    """Get a single event by ID.

    Args:
        event_id: The ID of the event to retrieve.

    Returns:
        JSON response with event data or error.
    """
    try:
        db = JSONDatabase()
        event = db.get_item("EVENT", event_id)
        if event:
            current_app.logger.info(f"Fetched event ID {event_id}")
            return jsonify(event), 200
        current_app.logger.warning(f"Event ID {event_id} not found")
        return jsonify({"error": "Event not found"}), 404
    except Exception as e:
        current_app.logger.error(f"Error fetching event {event_id}: {str(e)}")
        return jsonify({"error": "Failed to fetch event", "details": str(e)}), 500

@events_bp.put('/<int:event_id>')
def update_event(event_id: int):
    """Update an existing event.

    Args:
        event_id: The ID of the event to update.

    Request Form:
        - image: (optional) New event image.
        - name_event: (optional) event name.
        - id_organisor: (optional) Manager ID.
        - hour: (optional) event hour.
        - place: (optional) event place.
        - date_begin: (optional) Start date.
        - date_end: (optional) End date.

    Returns:
        JSON response with status.
    """
    db = JSONDatabase()
    
    # Check if event exists
    event = db.get_item("EVENT", event_id)
    if not event:
        current_app.logger.warning(f"event ID {event_id} not found")
        return jsonify({"error": "event not found"}), 404
    
    old_image_path = event.get("IMAGE", "")
    
    # Validate input data
    validation_errors = validate_event_data(request.form, require_all_fields=False)
    if validation_errors:
        return jsonify({"error": "Validation failed", "details": validation_errors}), 400
    
    # Prepare update data by merging with existing event
    update_data = event.copy()  # Start with existing record
    for field in ['name_event', 'hour', 'date_begin', 'date_end','place']:
        if field in request.form and request.form[field].strip():
            update_data[field.upper()] = request.form[field]
    if 'type_event' in request.form and request.form['type_event'].strip():
        update_data["TYPE_EV"] = request.form['type_event']
    if 'id_organisor' in request.form and request.form['id_organisor'].strip():
        update_data["ID_ORGANISOR"] = int(request.form['id_organisor'])
    
    
    # Handle file upload
    success, response, status_code = handle_image_upload(request, old_image_path, update_data)
    if not success:
        return jsonify(response), status_code
    
    # Check if there are any changes
    if update_data == event:
        current_app.logger.info(f"No changes provided for event ID {event_id}")
        return jsonify({"success": True, "message": "No changes provided"}), 200
    
    try:
        # Update event
        if not db.update_query("EVENT", event_id, update_data):
            current_app.logger.error(f"Failed to update event {event_id}: Record not found")
            return jsonify({"error": "event not found"}), 404
        
        # Remove old image after successful database update
        remove_old_image(old_image_path, update_data.get("IMAGE"))
        current_app.logger.info(f"Updated event ID {event_id} with data: {update_data}")
        
        # Verify updated record
        updated_event = db.get_item("EVENT", event_id)
        if not updated_event or updated_event.get("id") != event_id:
            current_app.logger.error(f"Updated event ID {event_id} is corrupted or missing")
            return jsonify({"error": "Event update failed due to data corruption"}), 500
        
        return jsonify({
            "success": True,
            "message": "event updated successfully",
            "event_id": event_id
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Error updating event {event_id}: {str(e)}")
        return jsonify({"error": "Failed to update event", "details": str(e)}), 500

@events_bp.delete('/<int:event_id>')
def delete_event(event_id: int):
    """Delete a event.

    Args:
        event_id: The ID of the event to delete.

    Returns:
        JSON response with status.
    """
    db = JSONDatabase()
    
    try:
        event = db.get_item("EVENT", event_id)
        if not event:
            current_app.logger.warning(f"event ID {event_id} not found")
            return jsonify({"error": "event not found"}), 404
        
        # Delete associated image
        if "IMAGE" in event:
            image_path = os.path.join("static", event["IMAGE"])
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                    current_app.logger.info(f"Removed image: {image_path}")
                except Exception as e:
                    current_app.logger.warning(f"Could not remove event image: {str(e)}")
        
        # Delete event
        if not db.delete_query("EVENT", event_id):
            current_app.logger.error(f"Failed to delete event {event_id}: Record not found")
            return jsonify({"error": "event not found"}), 404
        
        current_app.logger.info(f"Deleted event ID {event_id}")
        return jsonify({
            "success": True,
            "message": "event deleted successfully",
            "event_id": event_id
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Error deleting event {event_id}: {str(e)}")
        return jsonify({"error": "Failed to delete event", "details": str(e)}), 500

@events_bp.get('/items')
def get_multiple_events():
    """Get multiple events by their IDs.

    Request JSON:
        List of event IDs to retrieve.

    Returns:
        JSON list of requested events.
    """
    try:
        db = JSONDatabase()
        
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        event_ids = request.get_json()
        if not isinstance(event_ids, list):
            return jsonify({"error": "Expected array of event IDs"}), 400
        
        events = []
        for event_id in event_ids:
            try:
                event = db.get_item("EVENT", int(event_id))
                if event:
                    events.append(event)
            except ValueError:
                current_app.logger.warning(f"Invalid event ID: {event_id}")
                continue
        
        current_app.logger.info(f"Fetched {len(events)} events by IDs")
        return jsonify(events), 200
    
    except Exception as e:
        current_app.logger.error(f"Error fetching multiple events: {str(e)}")
        return jsonify({"error": "Failed to fetch events", "details": str(e)}), 500