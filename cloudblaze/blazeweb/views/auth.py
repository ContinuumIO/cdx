from cloudblaze.blazeweb.app import app
from flask import (
	render_template, request, current_app,
	send_from_directory, make_response, session, redirect, url_for)
import werkzeug.exceptions
import cloudblaze.blazeweb.models.user as user
import cloudblaze.blazeweb.models as models
import uuid


@app.route('/login', methods=['POST'])
def login():
    email, password = request.form['email'], request.form['password']
    try:
        usermodel = user.auth_user(current_app.model_redis, email, password)
        session['username'] = usermodel.email
        return 'success'
    except models.UnauthorizedException:
        raise werkzeug.exceptions.Unauthorized('bad login')
        
@app.route('/register', methods=['POST'])
def register():
    email, password = request.form['email'], request.form['password']    
    try:
        usermodel = user.new_user(current_app.model_redis, email, password,
                                  docs=[str(uuid.uuid4())])
        session['username'] = usermodel.email        
        return 'success'
    except models.UnauthorizedException:
        raise werkzeug.exceptions.Unauthorized('user already exists')
    
@app.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    session['foo'] = None
    return redirect('/')

