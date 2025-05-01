import os
import uuid
from datetime import datetime
from typing import Tuple, Optional, Dict, Any
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from Database.db import JSONDatabase

events_bp = Blueprint('events', __name__)
UPLOAD_FOLDER = os.path.join("static", "images", "uploads", "events")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'svg'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def is_allowed_file(filename: str) -> bool:
    """Check if the uploaded file has a valid extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_event_data(data: Dict[str, Any], require_all_fields: bool = True) -> list:
    """Validate event data before insertion or update."""
    required_fields = ['name_event', 'type_event', 'id_organisor', 'date_begin', 'hour', 'date_end', 'place']
    errors = []

    if require_all_fields:
        for field in required_fields:
            if field not in data or not str(data[field]).strip():
                errors.append(f"Missing or empty required field: {field}")

    # Validate hour
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
                errors.append("Organisor ID must be a positive integer")
        except ValueError:
            errors.append("Organisor ID must be a valid integer")

    # Validate description (optional, max 500 characters)
    if 'description' in data and data['description']:
        description = str(data['description']).strip()
        if len(description) > 500:
            errors.append("Description exceeds maximum length of 500 characters")

    return errors

def check_event_conflict(db: JSONDatabase, date_begin: str, place: str, exclude_event_id: Optional[int] = None) -> bool:
    """Check if an event conflicts with another event at the same date_begin and place."""
    conditions = {"DATE_BEGIN": date_begin, "PLACE": place}
    try:
        conflicting_events = db.select_query(table="EVENT",)
        
        for event in conflicting_events:
            if exclude_event_id is None or event.get("ID") != exclude_event_id:
                current_app.logger.info(f"Conflict found: Event ID {event.get('ID')} at {place} on {date_begin}")
                return True
        return False
    except Exception as e:
        current_app.logger.error(f"Error checking event conflict for {date_begin}, {place}: {str(e)}")
        raise

def handle_image_upload(
    request: Any, 
    old_image_path: Optional[str], 
    update_data: Dict[str, Any], 
    upload_folder: str = UPLOAD_FOLDER
) -> Tuple[bool, Optional[Dict[str, str]], Optional[int]]:
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
        image_path = f"images/uploads/events/{filename}"

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
        return False, {"error": "Failed to process image", "details": str(e)}, 500

def remove_old_image(old_image_path: Optional[str], new_image_path: Optional[str]):
    """Remove old image if it exists and is different from the new image."""
    if old_image_path and new_image_path and old_image_path != new_image_path:
        old_file_path = os.path.join("fr/static", old_image_path)
        if os.path.exists(old_file_path):
            try:
                os.remove(old_file_path)
                current_app.logger.info(f"Removed old image: {old_file_path}")
            except Exception as e:
                current_app.logger.warning(f"Could not remove old image {old_file_path}: {str(e)}")
        else:
            current_app.logger.warning(f"Old image path does not exist: {old_file_path}")

@events_bp.post('/')
def create_event():
    """Create a new event with conflict checking."""
    db = JSONDatabase()
    
    validation_errors = validate_event_data(request.form)
    if validation_errors:
        return jsonify({"error": "Validation failed", "details": validation_errors}), 400
    
    update_data = {}
    for field in ['name_event', 'hour', 'date_begin', 'date_end', 'place', 'description']:
        if field in request.form and request.form[field].strip():
            update_data[field.upper()] = request.form[field]
    if 'type_event' in request.form and request.form['type_event'].strip():
        update_data["TYPE_EV"] = request.form['type_event']
    if 'id_organisor' in request.form and request.form['id_organisor'].strip():
        try:
            update_data["ID_ORGANISOR"] = int(request.form['id_organisor'])
        except ValueError:
            return jsonify({"error": "Invalid id_organisor", "details": "Must be an integer"}), 400
    
    # Check for event conflict
    try:
        if check_event_conflict(db, update_data["DATE_BEGIN"], update_data["PLACE"]):
            return jsonify({
                "alert": "Conflict detected",
                "error": "Event conflict",
                "details": f"An event already exists at {update_data['PLACE']} on {update_data['DATE_BEGIN']}"
            }), 409
    except Exception as e:
        current_app.logger.error(f"Conflict check failed: {str(e)}")
        return jsonify({"error": "Failed to check conflicts", "details": str(e)}), 500
    
    success, response, status_code = handle_image_upload(request, None, update_data)
    if not success:
        return jsonify(response), status_code
    
    try:
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
    """Get all events."""
    try:
        db = JSONDatabase()
        events = db.select_query(table="EVENT")
        current_app.logger.info(f"Fetched {len(events)} events")
        return jsonify(events), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching events: {str(e)}")
        return jsonify({"error": "Failed to fetch events", "details": str(e)}), 500

@events_bp.get('/<int:event_id>')
def get_event(event_id: int):
    """Get a single event by ID."""
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
    """Update an existing event with conflict checking."""
    db = JSONDatabase()
    
    try:
        event = db.get_item("EVENT", event_id)
        if not event:
            current_app.logger.warning(f"Event ID {event_id} not found")
            return jsonify({"error": "Event not found"}), 404
        
        old_image_path = event.get("IMAGE", "")
        
        validation_errors = validate_event_data(request.form, require_all_fields=False)
        if validation_errors:
            return jsonify({"error": "Validation failed", "details": validation_errors}), 400
        
        update_data = event.copy()
        for field in ['name_event', 'hour', 'date_begin', 'date_end', 'place', 'description']:
            if field in request.form and request.form[field].strip():
                update_data[field.upper()] = request.form[field]
        if 'type_event' in request.form and request.form['type_event'].strip():
            update_data["TYPE_EV"] = request.form['type_event']
        if 'id_organisor' in request.form and request.form['id_organisor'].strip():
            try:
                update_data["ID_ORGANISOR"] = int(request.form['id_organisor'])
            except ValueError:
                return jsonify({"error": "Invalid id_organisor", "details": "Must be an integer"}), 400
        
        # Check for event conflict, excluding the current event
        if ('DATE_BEGIN' in update_data or 'PLACE' in update_data) and \
           check_event_conflict(db, update_data["DATE_BEGIN"], update_data["PLACE"], exclude_event_id=event_id):
            return jsonify({
                "alert": "Conflict detected",
                "error": "Event conflict",
                "details": f"An event already exists at {update_data['PLACE']} on {update_data['DATE_BEGIN']}"
            }), 409
        
        success, response, status_code = handle_image_upload(request, old_image_path, update_data)
        if not success:
            return jsonify(response), status_code
        
        if update_data == event:
            current_app.logger.info(f"No changes provided for event ID {event_id}")
            return jsonify({"success": True, "message": "No changes provided"}), 200
        
        if not db.update_query("EVENT", event_id, update_data):
            current_app.logger.error(f"Failed to update event {event_id}: Record not found")
            return jsonify({"error": "Event not found"}), 404
        
        remove_old_image(old_image_path, update_data.get("IMAGE"))
        current_app.logger.info(f"Updated event ID {event_id} with data: {update_data}")
        
        updated_event = db.get_item("EVENT", event_id)
        if not updated_event or updated_event.get("ID") != event_id:
            current_app.logger.error(f"Updated event ID {event_id} is corrupted or missing")
            return jsonify({"error": "Event update failed due to data corruption"}), 500
        
        return jsonify({
            "success": True,
            "message": "Event updated successfully",
            "event_id": event_id
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Error updating event {event_id}: {str(e)}")
        return jsonify({"error": "Failed to update event", "details": str(e)}), 500

@events_bp.delete('/<int:event_id>')
def delete_event(event_id: int):
    """Delete an event."""
    db = JSONDatabase()
    
    try:
        event = db.get_item("EVENT", event_id)
        if not event:
            current_app.logger.warning(f"Event ID {event_id} not found")
            return jsonify({"error": "Event not found"}), 404
        
        if "IMAGE" in event:
            image_path = os.path.join("fr/static", event["IMAGE"])
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                    current_app.logger.info(f"Removed image: {image_path}")
                except Exception as e:
                    current_app.logger.warning(f"Could not remove event image: {str(e)}")
        
        if not db.delete_query("EVENT", event_id):
            current_app.logger.error(f"Failed to delete event {event_id}: Record not found")
            return jsonify({"error": "Event not found"}), 404
        
        current_app.logger.info(f"Deleted event ID {event_id}")
        return jsonify({
            "success": True,
            "message": "Event deleted successfully",
            "event_id": event_id
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Error deleting event {event_id}: {str(e)}")
        return jsonify({"error": "Failed to delete event", "details": str(e)}), 500

@events_bp.get('/items')
def get_multiple_events():
    """Get multiple events by their IDs."""
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