from datetime import datetime, timedelta
from flask import make_response, render_template, Blueprint, request, jsonify, redirect, send_file
from flask_jwt_extended import unset_jwt_cookies, jwt_required
from flask_jwt_extended import get_jwt_identity
from Database.db import JSONDatabase
from utils.config import Config
from dotenv import load_dotenv
import os


load_dotenv()

dashboard_bp = Blueprint('dashboard', __name__, template_folder='templates', static_folder='static')


@dashboard_bp.route('/')
@jwt_required(optional=True)
def index():
    current_user = get_jwt_identity()
    if current_user:
        return redirect('/dashboard/projects')
    return redirect('/dashboard/login')

@dashboard_bp.route('/login', methods=['GET'])
@jwt_required(optional=True)
def login():
    current_user = get_jwt_identity()
    if current_user:
        return redirect('/dashboard/projects')
    return render_template('login.html')
# dashboard.py (updated)

from flask_jwt_extended import get_jwt_identity, get_jwt

# ... existing imports ...

@dashboard_bp.get('/projects')
@jwt_required()
def projects():
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role', 'user')  

    db = JSONDatabase()
    if role == 'admin':
        projects = db.select_query("PROJECT")
    else:
        # Fetch projects associated with the current researcher
        projects = db.select_filter("PROJECT", {"ID_MANAGER": current_user_id})
        researchers = db.select_query("RESEARCHER")
        return render_template('profile.html', title='Projects', projects=projects, researchers=researchers)
    researchers = db.select_query("RESEARCHER")
    return render_template('projects.dashboard.html', title='Projects', projects=projects, researchers=researchers)

@dashboard_bp.get('/publications')
@jwt_required()
def publications():
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role', 'user')

    if role == 'admin':
        db = JSONDatabase()
        publications = db.select_query("PUBLICATION")
        researchers = db.select_query("RESEARCHER")
    else:
        db = JSONDatabase()
        # Fetch publications associated with the current researcher
        publications = db.select_filter("PUBLICATION",{"ID_RESEARCHER": current_user_id})
        researchers = db.select_filter( "RESEARCHER" , {"id": current_user_id})
        print(researchers)
        print(publications)
    return render_template('publications.dashboard.html', title='Publications', publications=publications , researchers=researchers)

@dashboard_bp.get('/events')
@jwt_required()
def events():
    db = JSONDatabase()
    events = db.select_query("EVENT")
    researchers = db.select_query("RESEARCHER")
    ev_types = db.select_query("TYPE_EV")
    return render_template('events.dashboard.html', title='Events', events=events , researchers=researchers , ev_types=ev_types)



@dashboard_bp.get('/partners')
@jwt_required()
def partners():
    db = JSONDatabase()
    partners = db.select_query("partners")
    researchers=db.select_query("RESEARCHER")
    return render_template('partners.dashboard.html', title='Partners', partners=partners)

@dashboard_bp.get('/researchers')
@jwt_required()
def researchers():
    db = JSONDatabase()
    researchers = db.select_query("RESEARCHER")
    return render_template('researchers.dashboard.html', title='Researchers', researchers=researchers)

@dashboard_bp.get('/equipements')
@jwt_required()
def equipments():
    db = JSONDatabase()
    equipments = db.select_query("equipements")
    return render_template('equipements.dashboard.html', title='Equipments', equipments=equipments)

@dashboard_bp.get("/logout")
def logout():
    # Create a response object to redirect the user
    response = make_response(redirect("/dashboard/login"))
    
    # Use unset_jwt_cookies to remove the JWT token from cookies
    unset_jwt_cookies(response)
    
    return response
