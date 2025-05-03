import os
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from Database.db import JSONDatabase

publication = Blueprint('publication', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'svg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@publication.route('/create_publication', methods=['POST'])
def create_publication():
    try:
        title = request.form.get('title')
        id_researcher = request.form.get('id_researcher')
        description = request.form.get('description')
        link = request.form.get('link')
        date_str = request.form.get('date')

        if not title or not id_researcher or not description or not date_str:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid date format'}), 400

        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(image_path)
                image_path = f'static/uploads/publications/{filename}'

        publication = Publication(
            title=title,
            id_researcher=id_researcher,
            description=description,
            link=link,
            date=date,
            image=image_path
        )
        
        db.session.add(publication)
        db.session.commit()
        
        return jsonify({'success': True}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@publication.route('/api/publication/<int:id>', methods=['PUT'])
def update_publication(id):
    try:
        publication = Publication.query.get_or_404(id)
        
        title = request.form.get('title')
        id_researcher = request.form.get('id_researcher')
        description = request.form.get('description')
        link = request.form.get('link')
        date_str = request.form.get('date')

        if not title or not id_researcher or not description or not date_str:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid date format'}), 400

        publication.title = title
        publication.id_researcher = id_researcher
        publication.description = description
        publication.link = link
        publication.date = date

        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(image_path)
                publication.image = f'static/uploads/publications/{filename}'

        db.session.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@publication.route('/api/publication/<int:id>', methods=['DELETE'])
def delete_publication(id):
    try:
        publication = Publication.query.get_or_404(id)
        
        if publication.image and os.path.exists(publication.image):
            os.remove(publication.image)
        
        db.session.delete(publication)
        db.session.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500