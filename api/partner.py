from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import current_user
from Database.db import JSONDatabase
from datetime import datetime
from typing import Dict, Any

partners_bp = Blueprint('partners', __name__)

def validate_partner_data(data: Dict[str, Any], require_all_fields: bool = True) -> list:
    """Validate partner data before insertion or update."""
    required_fields = ['name_partner', 'email_partner', 'phone', 'address', 'creation_date', 'amount']
    errors = []

    if require_all_fields:
        for field in required_fields:
            if field not in data or not str(data[field]).strip():
                errors.append(f"Missing or empty required field: {field}")

    # Validate email format
    if 'email_partner' in data and data['email_partner']:
        email = str(data['email_partner']).strip()
        if '@' not in email or '.' not in email:
            errors.append("Invalid email format")

    # Validate phone
    if 'phone' in data and data['phone']:
        try:
            phone = str(data['phone']).strip()
            if not phone.isdigit() or len(phone) < 7:
                errors.append("Invalid phone number. Must be digits only and at least 7 digits")
        except ValueError:
            errors.append("Invalid phone number")

    # Validate creation date
    if 'creation_date' in data and data['creation_date']:
        try:
            datetime.strptime(data['creation_date'], '%Y-%m-d')
        except ValueError:
            errors.append("Invalid date format for creation_date. Use YYYY-MM-DD")

    # Validate website (optional)
    if 'website' in data and data['website']:
        website = str(data['website']).strip()
        if not (website.startswith('http://') or website.startswith('https://')):
            errors.append("Website must start with http:// or https://")

    # Validate notes (optional, max 500 characters)
    if 'notes' in data and data['notes']:
        notes = str(data['notes']).strip()
        if len(notes) > 500:
            errors.append("Notes exceed maximum length of 500 characters")

    # Validate amount
    if 'amount' in data and data['amount']:
        try:
            amount = float(data['amount'])
            if amount < 0:
                errors.append("Amount must be a non-negative number")
        except (ValueError, TypeError):
            errors.append("Invalid amount. Must be a valid number")

    return errors

@partners_bp.post('/')
def create_partner():
    """Create a new partner."""
    db = JSONDatabase()

    validation_errors = validate_partner_data(request.form)
    if validation_errors:
        return jsonify({"error": "Validation failed", "details": validation_errors}), 400

    update_data = {}
    for field in ['name_partner', 'email_partner', 'phone', 'address', 'creation_date', 'website', 'notes', 'amount']:
        if field in request.form and request.form[field].strip():
            update_data[field.upper()] = request.form[field]
            if field == 'amount':
                update_data[field.upper()] = float(request.form[field])
            if field == 'phone':
                update_data[field.upper()] = int(request.form[field])

    try:
        partner_id = db.insert_query("PARTNER", update_data)
        current_app.logger.info(f"Created partner ID {partner_id} with data: {update_data}")

        return jsonify({
            "success": True,
            "message": "Partner created successfully",
            "partner_id": partner_id
        }), 201

    except Exception as e:
        current_app.logger.error(f"Error creating partner: {str(e)}")
        return jsonify({"error": "Failed to create partner", "details": str(e)}), 500

@partners_bp.get('/')
def get_partners():
    """Get all partners."""
    try:
        db = JSONDatabase()
        partners = db.select_query("PARTNER")
        current_app.logger.info(f"Fetched {len(partners)} partners")
        return jsonify(partners), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching partners: {str(e)}")
        return jsonify({"error": "Failed to fetch partners", "details": str(e)}), 500

@partners_bp.get('/<int:partner_id>')
def get_partner(partner_id: int):
    """Get a single partner by ID."""
    try:
        db = JSONDatabase()
        partner = db.get_item("PARTNER", partner_id)
        if partner:
            current_app.logger.info(f"Fetched partner ID {partner_id}")
            return jsonify(partner), 200
        current_app.logger.warning(f"Partner ID {partner_id} not found")
        return jsonify({"error": "Partner not found"}), 404
    except Exception as e:
        current_app.logger.error(f"Error fetching partner {partner_id}: {str(e)}")
        return jsonify({"error": "Failed to fetch partner", "details": str(e)}), 500

@partners_bp.put('/<int:partner_id>')
def update_partner(partner_id: int):
    """Update an existing partner."""
    db = JSONDatabase()

    try:
        partner = db.get_item("PARTNER", partner_id)
        if not partner:
            current_app.logger.warning(f"Partner ID {partner_id} not found")
            return jsonify({"error": "Partner not found"}), 404

        validation_errors = validate_partner_data(request.form, require_all_fields=False)
        if validation_errors:
            return jsonify({"error": "Validation failed", "details": validation_errors}), 400

        update_data = partner.copy()
        for field in ['name_partner', 'email_partner', 'phone', 'address', 'creation_date', 'website', 'notes', 'amount']:
            if field in request.form and request.form[field].strip():
                update_data[field.upper()] = request.form[field]
                if field == 'amount':
                    update_data[field.upper()] = float(request.form[field])
                if field == 'phone':
                    update_data[field.upper()] = int(request.form[field])

        if update_data == partner:
            current_app.logger.info(f"No changes provided for partner ID {partner_id}")
            return jsonify({"success": True, "message": "No changes provided"}), 200

        if not db.update_query("PARTNER", partner_id, update_data):
            current_app.logger.error(f"Failed to update partner {partner_id}: Record not found")
            return jsonify({"error": "Partner not found"}), 404

        current_app.logger.info(f"Updated partner ID {partner_id} with data: {update_data}")

        updated_partner = db.get_item("PARTNER", partner_id)
        if not updated_partner or updated_partner.get("id") != partner_id:
            current_app.logger.error(f"Updated partner ID {partner_id} is corrupted or missing")
            return jsonify({"error": "Partner update failed due to data corruption"}), 500

        return jsonify({
            "success": True,
            "message": "Partner updated successfully",
            "partner_id": partner_id
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error updating partner {partner_id}: {str(e)}")
        return jsonify({"error": "Failed to update partner", "details": str(e)}), 500

@partners_bp.delete('/<int:partner_id>')
def delete_partner(partner_id: int):
    """Delete a partner."""
    db = JSONDatabase()

    try:
        partner = db.get_item("PARTNER", partner_id)
        if not partner:
            current_app.logger.warning(f"Partner ID {partner_id} not found")
            return jsonify({"error": "Partner not found"}), 404

        if not db.delete_query("PARTNER", partner_id):
            current_app.logger.error(f"Failed to delete partner {partner_id}: Record not found")
            return jsonify({"error": "Partner not found"}), 404

        current_app.logger.info(f"Deleted partner ID {partner_id}")
        return jsonify({
            "success": True,
            "message": "Partner deleted successfully",
            "partner_id": partner_id
        }), 200

    except Exception as e:
        current_app.logger.error(f"Error deleting partner {partner_id}: {str(e)}")
        return jsonify({"error": "Failed to delete partner", "details": str(e)}), 500

@partners_bp.get('/items')
def get_multiple_partners():
    """Get multiple partners by their IDs."""
    try:
        db = JSONDatabase()

        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400

        partner_ids = request.get_json()
        if not isinstance(partner_ids, list):
            return jsonify({"error": "Expected array of partner IDs"}), 400

        partners = []
        for partner_id in partner_ids:
            try:
                partner = db.get_item("PARTNER", int(partner_id))
                if partner:
                    partners.append(partner)
            except ValueError:
                current_app.logger.warning(f"Invalid partner ID: {partner_id}")
                continue

        current_app.logger.info(f"Fetched {len(partners)} partners by IDs")
        return jsonify(partners), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching multiple partners: {str(e)}")
        return jsonify({"error": "Failed to fetch partners", "details": str(e)}), 500