from datetime import datetime, timedelta
from flask import make_response, render_template, Blueprint, request, jsonify, redirect, send_file
from flask_jwt_extended import unset_jwt_cookies
import requests
from Database.db import JSONDatabase
from utils.config import Config
from dotenv import load_dotenv
import os


load_dotenv()

dashboard_bp = Blueprint('dashboard', __name__, template_folder='templates', static_folder='static')

TOKEN = os.getenv('TOKEN')

@dashboard_bp.route('/')
def index():
    if request.cookies.get(TOKEN):
        return redirect('/dashboard/projects')
    return redirect('/dashboard/login')

@dashboard_bp.route('/login', methods=['GET'])
def login():
    print(request.cookies.get(TOKEN))
    if request.cookies.get(TOKEN):
        return redirect('/dashboard/projects')
    return render_template('login.html')

@dashboard_bp.get('/projects')
def projects():
    if request.cookies.get(TOKEN):
        db = JSONDatabase()
        projects = db.select_query("PROJECT")
        return render_template('projects.dashboard.html', title='Projects', projects=projects)
    return redirect('/dashboard/login')


@dashboard_bp.get('/events')
def events():
    if request.cookies.get(TOKEN):
        db = JSONDatabase()
        events = db.select_query("events")
        return render_template('events.dashboard.html', title='Events', events=events)
    return redirect('/dashboard/login')


@dashboard_bp.get('/publications')
def publications():
    if request.cookies.get(TOKEN):
        db = JSONDatabase()
        publications = db.select_query("publications")
        return render_template('publications.dashboard.html', title='Publications', publications=publications)
    return redirect('/dashboard/login')

@dashboard_bp.get('/partners')
def partners():
    if request.cookies.get(TOKEN):
        db = JSONDatabase()
        partners = db.select_query("partners")
        return render_template('partners.dashboard.html', title='Partners', partners=partners)
    return redirect('/dashboard/login')

@dashboard_bp.get('/researchers')
def researchers():
    if request.cookies.get(TOKEN):
        db = JSONDatabase()
        researchers = db.select_query("researchers")
        return render_template('researchers.dashboard.html', title='Researchers', researchers=researchers)
    return redirect('/dashboard/login')


@dashboard_bp.get('/equipements')
def equipments():
    if request.cookies.get(TOKEN):
        db = JSONDatabase()
        equipments = db.select_query("equipements")
        return render_template('equipements.dashboard.html', title='Equipments', equipments=equipments)
    return redirect('/dashboard/login')

@dashboard_bp.get("/logout")
def logout():
    # Create a response object to redirect the user
    response = make_response(redirect("/dashboard/login"))
    
    # Use unset_jwt_cookies to remove the JWT token from cookies
    unset_jwt_cookies(response)
    
    return response



