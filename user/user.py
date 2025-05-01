from datetime import datetime, timedelta
from flask import make_response, render_template, Blueprint, request, jsonify, redirect, send_file
from flask_jwt_extended import unset_jwt_cookies
from Database.db import JSONDatabase
from utils.config import Config
from dotenv import load_dotenv
import os


load_dotenv()

user_bp = Blueprint('user', __name__, template_folder='templates', static_folder='static')

TOKEN = os.getenv('TOKEN')

@user_bp.route('/')
def index():
    if request.cookies.get(TOKEN):
        return redirect('/user/projects')
    return redirect('/user/login')

@user_bp.route('/login', methods=['GET'])
def login():
    print(request.cookies.get(TOKEN))
    if request.cookies.get(TOKEN):
        return redirect('/user/projects')
    return render_template('login.html')

@user_bp.get('/projects')
def projects():
    if request.cookies.get(TOKEN):
        db = JSONDatabase()
        projects = db.select_query("PROJECT")
        researchers = db.select_query("RESEARCHER")
        return render_template('projects.user.html', title='Projects', projects=projects, researchers=researchers)
    return redirect('/user/login')


@user_bp.get('/events')
def events():
    if request.cookies.get(TOKEN):
        db = JSONDatabase()
        events = db.select_query("EVENT")
        researchers = db.select_query("RESEARCHER")
        ev_types = db.select_query("TYPE_EV")
        return render_template('events.user.html', title='Events', events=events , researchers=researchers , ev_types=ev_types)
    return redirect('/user/login')


@user_bp.get('/publications')
def publications():
    if request.cookies.get(TOKEN):
        db = JSONDatabase()
        publications = db.select_query("publications")
        return render_template('publications.user.html', title='Publications', publications=publications)
    return redirect('/user/login')

@user_bp.get('/partners')
def partners():
    if request.cookies.get(TOKEN):
        db = JSONDatabase()
        partners = db.select_query("partners")
        return render_template('partners.user.html', title='Partners', partners=partners)
    return redirect('/user/login')

@user_bp.get('/researchers')
def researchers():
    if request.cookies.get(TOKEN):
        db = JSONDatabase()
        researchers = db.select_query("researchers")
        return render_template('researchers.user.html', title='Researchers', researchers=researchers)
    return redirect('/user/login')


@user_bp.get('/equipements')
def equipments():
    if request.cookies.get(TOKEN):
        db = JSONDatabase()
        equipments = db.select_query("equipements")
        return render_template('equipements.user.html', title='Equipments', equipments=equipments)
    return redirect('/user/login')

@user_bp.get("/logout")
def logout():
    # Create a response object to redirect the user
    response = make_response(redirect("/user/login"))
    
    # Use unset_jwt_cookies to remove the JWT token from cookies
    unset_jwt_cookies(response)
    
    return response



