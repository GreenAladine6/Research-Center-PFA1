from flask import make_response, render_template, Blueprint, request, jsonify, redirect
from flask import Blueprint, request, jsonify, current_app
from Database.db import JSONDatabase
from utils.config import Config
from dotenv import load_dotenv
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import send_file
from flask import redirect, url_for

import os


load_dotenv()
# Load environment variables from .env file
# os.environ['API_URL'] = 'https://api.example.com'  # Example of setting an environment variable
# os.environ

fr_bp = Blueprint('fr', __name__, url_prefix='/', template_folder='templates', static_folder='static')


@fr_bp.route('/')
@fr_bp.route('/index')
@fr_bp.route('/home')
def index():
    response = redirect('/')
    response.set_cookie('lang', 'fr', max_age=60*60*24*30)
    if not request.cookies.get('lang'):
        return response
    db = JSONDatabase()
    projects = db.select_query("PROJECT")
    researchers=db.select_query("RESEARCHER")
    return render_template('index.html', projects=projects[:6], researchers=researchers[:6])



@fr_bp.get('/project')
def project():
    response = redirect('/project')
    response.set_cookie('lang', 'fr', max_age=60*60*24*30)
    if not request.cookies.get('lang'):
        return response
    db = JSONDatabase()
    projects = db.select_query("PROJECT")
    researchers = db.select_query("RESEARCHER")
    managers ={}
    for project in projects:
        for researcher in researchers:
            if project['ID_MANAGER'] == researcher['id']: 
                managers[project['ID_MANAGER']]=researcher['FULL_NAME']
    return render_template('project.html', pagetitle='Specialite', page='project', projects=projects , researchers=researchers , managers=managers)


@fr_bp.get('/events')  
def events():
    response = redirect('/events')
    response.set_cookie('lang', 'fr', max_age=60*60*24*30)
    if not request.cookies.get('lang'):
        return response
    db = JSONDatabase()
    events = db.select_query("EVENT")
    reseaerchers = db.select_query("RESEARCHER")
    return render_template('events.html', pagetitle='Evenements', page='events', events=events , researchers=reseaerchers)

@fr_bp.get('/staff')
def staff():
    response = redirect('/staff')
    response.set_cookie('lang', 'fr', max_age=60*60*24*30)
    if not request.cookies.get('lang'):
        return response
    db = JSONDatabase()
    researchers = db.select_query("RESEARCHER")
    return render_template('staff.html', pagetitle='Personnel', page='staff', researchers=researchers)

@fr_bp.get('/publications')
def publications():
    # Set language cookie if not set
    response = redirect('/publications')
    response.set_cookie('lang', 'fr', max_age=60*60*24*30)
    if not request.cookies.get('lang'):
        return response
    
    db = JSONDatabase()
    
    # Get publications and researchers
    publications = db.select_query("PUBLICATION")
    researchers = db.select_query("RESEARCHER")
    
    # Process publication dates
    for pub in publications:
        if pub.get('DATE_PUB'):
            try:
                # Convert string date to datetime object if needed
                if isinstance(pub['DATE_PUB'], str):
                    pub['DATE_OBJ'] = datetime.strptime(pub['DATE_PUB'], '%Y-%m-%d')
                else:
                    pub['DATE_OBJ'] = pub['DATE_PUB']
            except (ValueError, TypeError):
                pub['DATE_OBJ'] = None
        else:
            pub['DATE_OBJ'] = None
    
    return render_template('pubs.html',
                         pagetitle='Publications',
                         page='publications',
                         publications=publications,
                         researchers=researchers)


@fr_bp.get('/api/validate-researcher')
def validate_researcher():
    db = JSONDatabase()
    
    researcher_id = request.args.get('id', '').strip()
    researcher_name = request.args.get('name', '').strip()
    
    if not researcher_id or not researcher_name:
        return jsonify({'exists': False})
    
    try:
        # Check if researcher exists with this ID and name
        researcher = db.select_query(
            "RESEARCHER", 
            conditions=f"id = '{researcher_id}' AND FULL_NAME LIKE '%{researcher_name}%'"
        )
        
        if researcher and len(researcher) > 0:
            return jsonify({
                'exists': True,
                'researcher': {
                    'id': researcher[0]['id'],
                    'name': researcher[0]['FULL_NAME'],
                    'position': researcher[0].get('POSITION', '')
                }
            })
        return jsonify({'exists': False})
    except Exception as e:
        print(f"Error validating researcher: {e}")
        return jsonify({'exists': False})

@fr_bp.route('/add_publication', methods=['POST'])
def add_publication():
    db = JSONDatabase()
    
    try:
        # Get form data
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        link = request.form.get('link', '').strip()
        date_pub = request.form.get('DATE_PUB', '').strip()
        researcher_info = request.form.get('researcher_info', '').strip()
        image_file = request.files.get('image')

        # Validate required fields
        if not all([title, description, researcher_info]):
            return jsonify({
                'success': False,
                'message': 'Title, description, and researcher are required.'
            }), 400

        # Extract researcher ID from input (format: "ID - Full Name")
        match = re.match(r'^(\d+)\s*-\s*(.+)$', researcher_info)
        if not match:
            return jsonify({
                'success': False,
                'message': 'Invalid researcher format. Use "ID - Full Name".'
            }), 400

        researcher_id = match.group(1)

        # Validate and parse date
        try:
            pub_date = datetime.strptime(date_pub, '%Y-%m-%d') if date_pub else None
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Invalid date format. Use YYYY-MM-DD.'
            }), 400

        # Handle file upload
        image_path = None
        if image_file and image_file.filename:
            filename = secure_filename(image_file.filename)
            upload_dir = os.path.join(current_app.static_folder, 'images/uploads/publications')
            
            # Create directory if it doesn't exist
            os.makedirs(upload_dir, exist_ok=True)
            
            # Save file
            image_path = os.path.join('images/uploads/publications', filename)
            image_file.save(os.path.join(current_app.static_folder, image_path))

        # Create publication data
        new_publication = {
            'TITLE': title,
            'DESCRIPTION': description,
            'LINK': link or None,
            'DATE_PUB': pub_date.strftime('%Y-%m-%d') if pub_date else None,
            'ID_RESEARCHER': researcher_id,
            'IMAGE': image_path
        }

        # Insert into database
        db.insert("PUBLICATION", new_publication)

        return jsonify({
            'success': True,
            'message': 'Publication added successfully!'
        }), 201

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }), 500
    




@fr_bp.get('/about')
def about():
    response = redirect('/about')
    response.set_cookie('lang', 'fr', max_age=60*60*24*30)
    if not request.cookies.get('lang'):
        return response
    
    return render_template('about-us.html', pagetitle='A Propos', page='about')

@fr_bp.get('/contact')
def contact():
    response = redirect('/contact')
    response.set_cookie('lang', 'fr', max_age=60*60*24*30)
    if not request.cookies.get('lang'):
        return response
    return render_template('contact_us.html', pagetitle='Contactez-Nous', page='contact')
