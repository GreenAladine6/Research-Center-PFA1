import os
import uuid
from datetime import datetime
from typing import Tuple, Optional, Dict, Any
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from Database.db import JSONDatabase
from flask_login import current_user

event = Blueprint('event', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'svg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@event.route('/create_event', methods=['POST'])
def create_event():
    try:
        name_event = request.form.get('name_event')
        id_organisor = request.form.get('id_organisor')
        id_manager = request.form.get('id_manager')  # Should be current_user.id
        type_event = request.form.get('type_event')
        date_begin = request.form.get('date_begin')
        date_end = request.form.get('date_end')
        hour = request.form.get('hour')
        place = request.form.get('place')
        description = request.form.get('description')

        if not all([name_event, id_organisor, id_manager, type_event, date_begin, date_end, hour, place]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        try:
            date_beg = datetime.strptime(date_begin, '%Y-%m-%d').date()
            datend = datetime.strptime(date_end, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid date format'}), 400

        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(image_path)
                image_path = f'static/uploads/events/{filename}'

        event = Event(
            name_event=name_event,
            id_organisor=id_organisor,
            id_manager=current_user.id,  # Always set to current user
            type_ev=type_event,
            date_beg=date_beg,
            datend=datend,
            hour=hour,
            place=place,
            description=description,
            image=image_path
        )
        
        db.session.add(event)
        db.session.commit()
        
        return jsonify({'success': True}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@event.route('/api/events/<int:id>', methods=['PUT'])
def update_event(id):
    try:
        event = Event.query.get_or_404(id)
        
        if event.id_manager != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403

        name_event = request.form.get('name_event')
        id_organisor = request.form.get('id_organisor')
        type_event = request.form.get('type_event')
        date_begin = request.form.get('date_begin')
        date_end = request.form.get('date_end')
        hour = request.form.get('hour')
        place = request.form.get('place')
        description = request.form.get('description')

        if not all([name_event, id_organisor, type_event, date_begin, date_end, hour, place]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        try:
            date_beg = datetime.strptime(date_begin, '%Y-%m-%d').date()
            datend = datetime.strptime(date_end, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid date format'}), 400

        event.name_event = name_event
        event.id_organisor = id_organisor
        event.type_ev = type_event
        event.date_beg = date_beg
        event.datend = datend
        event.hour = hour
        event.place = place
        event.description = description

        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(image_path)
                event.image = f'static/uploads/events/{filename}'

        db.session.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@event.route('/api/events/<int:id>/quit', methods=['PATCH'])
def quit_event(id):
    try:
        event = Event.query.get_or_404(id)
        
        if event.id_manager != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403

        event.id_manager = None
        db.session.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500