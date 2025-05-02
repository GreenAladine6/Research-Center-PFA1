from flask import Blueprint, render_template, redirect, request, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity, unset_jwt_cookies
from Database.db import JSONDatabase
from dotenv import load_dotenv
import os

load_dotenv()

dashboard_bp = Blueprint('dashboard', __name__,
                        template_folder='templates',
                        static_folder='static')

def verify_user():
    identity = get_jwt_identity()
    return identity and identity.get('role') in ['admin', 'user']

@dashboard_bp.route('/')
def index():
    return redirect('/dashboard/login')

@dashboard_bp.route('/login', methods=['GET'])
def login():
    error = request.args.get('error', '')
    return render_template('login.html', error=error)

@dashboard_bp.get('/projects')
@jwt_required()
def projects():
    if not verify_user():
        return redirect('/dashboard/login?error=Unauthorized')
    
    db = JSONDatabase()
    return render_template('projects.dashboard.html',
                         projects=db.select_query("PROJECT"),
                         researchers=db.select_query("RESEARCHER"))


@dashboard_bp.get('/user')
@jwt_required()
def user_dashboard():
    current_user = get_current_user()
    if current_user['role'] != 'user':
        return redirect(url_for('dashboard.login', error='Accès non autorisé'))
    
    db = JSONDatabase()
    researcher = db.find_researcher_by_id(current_user['user_id'])
    return render_template('user.dashboard.html',
                         researcher=researcher,
                         current_user=current_user)

@dashboard_bp.get('/events')
def events():
    if request.cookies.get(TOKEN):
        db = JSONDatabase()
        events = db.select_query("EVENT")
        researchers = db.select_query("RESEARCHER")
        ev_types = db.select_query("TYPE_EV")
        return render_template('events.dashboard.html', title='Events', events=events , researchers=researchers , ev_types=ev_types)
    return redirect('/dashboard/login')


@dashboard_bp.get('/publications')
def publications():
    if request.cookies.get(TOKEN):
        db = JSONDatabase()
        publications = db.select_query("PUBLICATION")
        researchers = db.select_query("RESEARCHER")
        return render_template('publications.dashboard.html', title='Publications', publications=publications ,researchers=researchers)
    return redirect('/dashboard/login')

@dashboard_bp.get('/partners')
def partners():
    if request.cookies.get(TOKEN):
        db = JSONDatabase()
        partners = db.select_query("PARTNER")
        return render_template('partners.dashboard.html', title='Partners', partners=partners)
    return redirect('/dashboard/login')

@dashboard_bp.get('/researchers')
def researchers():
    if request.cookies.get(TOKEN):
        db = JSONDatabase()
        researchers = db.select_query("RESEARCHER")
        grades= db.select_query("GRADE")
        return render_template('researchers.dashboard.html', title='Researchers', researchers=researchers, grades=grades)
    return redirect('/dashboard/login')


@dashboard_bp.get('/equipements')
def equipments():
    if request.cookies.get(TOKEN):
        db = JSONDatabase()
        equipments = db.select_query("EQUIPEMENT")
        return render_template('equipements.dashboard.html', title='Equipments', equipments=equipments)
    return redirect('/dashboard/login')

@dashboard_bp.get("/logout")
def logout():
    response = make_response(redirect(url_for('dashboard.login')))
    unset_jwt_cookies(response)
    return response


