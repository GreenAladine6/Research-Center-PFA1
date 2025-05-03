from flask import Blueprint, request, jsonify, current_app
from Database.db import JSONDatabase
from datetime import datetime
from typing import Dict, Any

equipment_bp = Blueprint('equipment', __name__)

def validate_equipment_data(data: Dict[str, Any], require_all_fields: bool = True) -> list:
    """Validate equipment data before insertion or update."""
    required_fields = ['name_equipment', 'purchase_date', 'laboratoire_id']
    errors = []

    if require_all_fields:
        for field in required_fields:
            if field not in data or not str(data[field]).strip():
                errors.append(f"Missing or empty required field: {field}")

    # Validate purchase date
    if 'purchase_date' in data and data['purchase_date']:
        try:
            datetime.strptime(data['purchase_date'], '%Y-%m-d')
        except ValueError:
            errors.append("Invalid date format for purchase_date. Use YYYY-MM-DD")

    # Validate laboratoire_id
    if 'laboratoire_id' in data and data['laboratoire_id']:
        try:
            laboratoire_id = int(data['laboratoire_id'])
            if laboratoire_id <= 0:
                errors.append("Laboratory ID must be a positive integer")
        except ValueError:
            errors.append("Laboratory ID must be a valid integer")

    return errors

@equipment_bp.post('/')
def create_equipment():
    """Create a new equipment."""
    db = JSONDatabase()

    validation_errors = validate_equipment_data(request.form)
    if validation_errors:
        return jsonify({"error": "Validation failed", "details": validation_errors}), 400

    update_data = {}
    for field in ['name_equipment', 'purchase_date']:
        if field in request.form and request.form[field].strip():
            update_data[field.upper()] = request.form[field]
    if 'laboratoire_id' in request.form and request.form['laboratoire_id'].strip():
        try:
            update_data["LABORATOIRE_ID"] = int(request.form['laboratoire_id'])
        except ValueError:
            return jsonify({"error": "Invalid laboratoire_id", "details": "Must be an integer"}), 400

    try:
        equipment_id = db.insert_query("EQUIPMENT", update_data)
        current_app.logger.info(f"Created equipment ID {equipment_id} with data: {update_data}")

        return jsonify({
            "success": True,
            "message": "Equipment created successfully",
            "equipment_id": equipment_id
        }), 201

    except Exception as e:
        current_app.logger.error(f"Error creating equipment: {str(e)}")
        return jsonify({"error": "Failed to create equipment", "details": str(e)}), 500

@equipment_bp.get('/')
def get_equipment():
    """Get all equipment."""
    try:
        db = JSONDatabase()
        equipment = db.select_query("EQUIPMENT")
        current_app.logger.info(f"Fetched {len(equipment)} equipment")
        return jsonify(equipment), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching equipment: {str(e)}")
        return jsonify({"error": "Failed to fetch equipment", "details": str(e)}), 500

@equipment_bp.get('/<int:equipment_id>')
def get_equipment_item(equipment_id: int):
    """Get a single equipment by ID."""
    try:
        db = JSONDatabase()
        equipment = db.get_item("EQUIPMENT", equipment_id)
        if equipment:
            current_app.logger.info(f"Fetched equipment ID {equipment_id}")
            return jsonify(equipment), 200
        current_app.logger.warning(f"Equipment ID {equipment_id} not found")
        return jsonify({"error": "Equipment not found"}), 404
    except Exception as e:
        current_app.logger.error(f"Error fetching equipment {equipment_id}: {str(e)}")
        return jsonify({"error": "Failed to fetch equipment", "details": str(e)}), 500

@equipment_bp.put('/<int:equipment_id>')
def update_equipment(equipment_id: int):
    """Update an existing equipment."""
    db = JSONDatabase()

    try:
        equipment = db.get_item("EQUIPMENT", equipment_id)
        if not equipment:
            current_app.logger.warning(f"Equipment ID {equipment_id} not found")
            return jsonify({"error": "Equipment not found"}), 404

        validation_errors = validate_equipment_data(request.form, require_all_fields=False)
        if validation_errors:
            return jsonify({"error": "Validation failed", "details": validation_errors}), 400

        update_data = equipment.copy()
        for field in ['name_equipment', 'purchase_date']:
            if field in request.form and request.form[field].strip():
                update_data[field.upper()] = request.form[field]
        if 'laboratoire_id' in request.form and request.form['laboratoire_id'].strip():
            try:
                update_data["LABORATOIRE_ID"] = int(request.form['laboratoire_id'])
            except ValueError:
                return jsonify({"error": "Invalid laboratoire_id", "details": "Must be an integer"}), 400

        if update_data == equipment:
            current_app.logger.info(f"No changes provided for equipment ID {equipment_id}")
            return jsonify({"success": True, "message": "No changes provided"}), 200

        if not db.update_query("EQUIPMENT", equipment_id, update_data):
            current_app.logger.error(f"Failed to update equipment {equipment_id}: Record not found")
            return jsonify({"error": "Equipment not found"}), 404

        current_app.logger.info(f"Updated equipment ID {equipment_id} with data: {update_data}")

        updated_equipment = db.get_item("EQUIPMENT", equipment_id)
        if not updated_equipment or updated_equipment.get("id") != equipment_id:
            current_app.logger.error(f"Updated equipment ID {equipment_id} is corrupted or missing")
            return jsonify({"error": "Equipment update failed due to data corruption"}), 500

        return jsonify({
            "success": True,
            "message": "Equipment updated successfully",
            "equipment_id": equipment_id
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error updating equipment {equipment_id}: {str(e)}")
        return jsonify({"error": "Failed to update equipment", "details": str(e)}), 500

@equipment_bp.delete('/<int:equipment_id>')
def delete_equipment(equipment_id: int):
    """Delete an equipment."""
    db = JSONDatabase()

    try:
        equipment = db.get_item("EQUIPMENT", equipment_id)
        if not equipment:
            current_app.logger.warning(f"Equipment ID {equipment_id} not found")
            return jsonify({"error": "Equipment not found"}), 404

        if not db.delete_query("EQUIPMENT", equipment_id):
            current_app.logger.error(f"Failed to delete equipment {equipment_id}: Record not found")
            return jsonify({"error": "Equipment not found"}), 404

        current_app.logger.info(f"Deleted equipment ID {equipment_id}")
        return jsonify({
            "success": True,
            "message": "Equipment deleted successfully",
            "equipment_id": equipment_id
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error deleting equipment {equipment_id}: {str(e)}")
        return jsonify({"error": "Failed to delete equipment", "details": str(e)}), 500

@equipment_bp.get('/items')
def get_multiple_equipment():
    """Get multiple equipment by their IDs."""
    try:
        db = JSONDatabase()

        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400

        equipment_ids = request.get_json()
        if not isinstance(equipment_ids, list):
            return jsonify({"error": "Expected array of equipment IDs"}), 400

        equipment = []
        for equipment_id in equipment_ids:
            try:
                item = db.get_item("EQUIPMENT", int(equipment_id))
                if item:
                    equipment.append(item)
            except ValueError:
                current_app.logger.warning(f"Invalid equipment ID: {equipment_id}")
                continue

        current_app.logger.info(f"Fetched {len(equipment)} equipment by IDs")
        return jsonify(equipment), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching multiple equipment: {str(e)}")
        return jsonify({"error": "Failed to fetch equipment", "details": str(e)}), 500