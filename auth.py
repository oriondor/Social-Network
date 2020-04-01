from flask import Blueprint, render_template, request, redirect, url_for, make_response
import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token,create_refresh_token,set_access_cookies,unset_jwt_cookies,set_refresh_cookies
from application import mongo, jwt

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['POST','GET'])
def login():
	if 'errors' not in request.args:
		errors=[]
	else:
		errors = [request.args.get('errors')]
	if request.method=="POST":
		username = request.form.get('username')
		password = request.form.get('password')
		try:
			user = mongo.db.users.find_one_or_404({'username':username})
			if check_password_hash(user['password'],password):
				mongo.db.users.update_one({'username':user['username']},{'$set':{'last_logged':datetime.datetime.now()}})
				access_token = create_access_token(identity=username)
				refresh_token = create_refresh_token(identity=username)
				#print('tokens are ', access_token, refresh_token)
				#session['user_info'] = user
				resp = make_response(redirect(url_for('home')))
				set_access_cookies(resp, access_token)
				set_refresh_cookies(resp, refresh_token)
				return resp
			errors.append('Password is incorrect')
		except Exception as e:
			errors.append(f'User not found {e}')
	return render_template('login.html', errors=errors)


@auth.route('/register', methods=['POST','GET'])
def register():
	errors = []
	if request.method=="POST":
		username = request.form.get('username')
		try:
			mongo.db.users.find_one_or_404({'username':username})
			errors.append("User already exists")
		except Exception as e:
			password = request.form.get('password')
			confirm = request.form.get('confirm')
			if password==confirm:
				user = {'username':username,
				'password':generate_password_hash(password),
				'photo_name':"profile_standart.jpeg"}
				mongo.db.users.insert_one(user)
				return redirect(url_for('auth.login'))
			else:
				errors.append('Passwords do not match')
	return render_template('register.html',errors=errors)

@auth.route('/logout')
def logout():
	#session.pop('user_info',None)
	resp = make_response(redirect(url_for('home')))
	unset_jwt_cookies(resp)
	return resp