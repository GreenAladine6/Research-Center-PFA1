from flask import make_response, render_template, Blueprint, request, jsonify, redirect
import requests
from Database.db import JSONDatabase
from utils.config import Config
from dotenv import load_dotenv
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
    projects = db.select_query("PROJECTS")
    return render_template('index.html', projects=projects[:6], page='')



@fr_bp.get('/project')
def project():
    response = redirect('/project')
    response.set_cookie('lang', 'fr', max_age=60*60*24*30)
    if not request.cookies.get('lang'):
        return response
    db = JSONDatabase()
    projects = db.select_query("PROJECTS")
    return render_template('project.html', pagetitle='Specialite', page='project', projects=projects)


@fr_bp.get('/events')  
def events():
    response = redirect('/events')
    response.set_cookie('lang', 'fr', max_age=60*60*24*30)
    if not request.cookies.get('lang'):
        return response
    db = JSONDatabase()
    events = db.select_query("EVENTS")
    return render_template('events.html', pagetitle='Evenements', page='events', events=events)

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
    response = redirect('/publications')
    response.set_cookie('lang', 'fr', max_age=60*60*24*30)
    if not request.cookies.get('lang'):
        return response
    db = JSONDatabase()
    publications = db.select_query("PUBLICATION")
    return render_template('pubs.html', pagetitle='Publications', page='publications', publications=publications)
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
