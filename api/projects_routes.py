import os
import uuid
from datetime import datetime
from typing import Tuple, Optional, Dict, Any
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from Database.db import JSONDatabase
from flask_login import current_user

projects = Blueprint('projects', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'svg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@projects.route('/create_project', methods=['POST'])
def create_project():
    try:
        name_project = request.form.get('name_project')
        budget = request.form.get('budget')
        date_begin = request.form.get('date_begin')
        date_end = request.form.get('date_end')
        state = request.form.get('state')

        if not all([name_project, budget, date_begin, date_end, state]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        try:
            budget = float(budget)
            date_beg = datetime.strptime(date_begin, '%Y-%m-%d').date()
            date_end = datetime.strptime(date_end, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid date or budget format'}), 400

        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(image_path)
                image_path = f'static/uploads/projects/{filename}'

        project = Project(
            name_project=name_project,
            id_manager=current_user.id,  # Always set to current user
            budget=budget,
            date_begin=date_beg,
            date_end=date_end,
            state=state,
            image=image_path
        )
        
        db.session.add(project)
        db.session.commit()
        
        return jsonify({'success': True}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@projects.route('/api/projects/<int:id>', methods=['PUT'])
def update_project(id):
    try:
        project = Project.query.get_or_404(id)
        
        if project.id_manager != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403

        name_project = request.form.get('name_project')
        budget = request.form.get('budget')
        date_begin = request.form.get('date_begin')
        date_end = request.form.get('date_end')
        state = request.form.get('state')

        if not all([name_project, budget, date_begin, date_end, state]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        try:
            budget = float(budget)
            date_beg = datetime.strptime(date_begin, '%Y-%m-%d').date()
            date_end = datetime.strptime(date_end, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid date or budget format'}), 400

        project.name_project = name_project
        project.budget = budget
        project.date_begin = date_beg
        project.date_end = date_end
        project.state = state

        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(image_path)
                project.image = f'static/uploads/projects/{filename}'

        db.session.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@projects.route('/api/projects/<int:id>/quit', methods=['PATCH'])
def quit_project(id):
    try:
        project = Project.query.get_or_404(id)
        
        if project.id_manager != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403

        project.id_manager = None
        db.session.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500