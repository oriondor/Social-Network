from flask import Flask, render_template, request, redirect, url_for
import datetime
from database import mongo
from jwt_ext import jwt
from bson.objectid import ObjectId
import datetime
#import jwt
#from functools import wraps
from flask_jwt_extended import (jwt_required,jwt_optional, create_access_token,
	get_jwt_identity
)

import config
from random_string import randomString

from auth import auth
from profile import profile_bpt
from api import api_bpt


app = Flask(__name__)
app.config['MONGO_URI'] = config.mongo_uri
app.config['JSON_SORT_KEYS'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True
mongo.init_app(app)
app.config['JWT_SECRET_KEY'] = 'thisisthesercetkey'  
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
#app.config['JWT_ACCESS_COOKIE_PATH'] = '/api/'
#app.config['JWT_REFRESH_COOKIE_PATH'] = '/token/refresh'
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
jwt.init_app(app)

def register_blueprints(app):
	app.register_blueprint(auth)
	app.register_blueprint(profile_bpt)
	app.register_blueprint(api_bpt)
register_blueprints(app)

def log_activity(username,activity):
	print(activity)
	log_activity = mongo.db.users.find_one_or_404({'username':username})['log_activity']
	log_activity.update(activity)
	mongo.db.users.update_one({'username':username},{'$set':{'log_activity':log_activity}})

@jwt.expired_token_loader
def my_expired_token_callback(expired_token):
    token_type = expired_token['type']
    return redirect(url_for('auth.login', errors="Войдите заново"))


@app.route('/')
@jwt_optional
def home():
	current_user=get_jwt_identity()
	print('current_user = ',current_user)
	return render_template('home.html',user_info=current_user)

@app.route('/new_post', methods=['POST','GET'])
@jwt_required
def new_post():
	current_user = get_jwt_identity()
	print("current user is", current_user)
	if current_user and request.method=="POST":
		if request.form.get('add_post'):
			text = request.form.get('new_text')
			filename = [0,0,'0']
			if 'new_photo' in request.files:
				file = request.files['new_photo']
				if file.filename!='':
					filename = file.filename.split('.')
					filename.append(f"{filename[0]}-{randomString(5)}.{filename[1]}")
					file_id = mongo.save_file(filename[2],file)
			print(filename)
			date_now = datetime.datetime.now()
			likes={}
			post={
			'text':text,
			'photo_name':filename[2],
			'author':current_user,
			'likes':0,
			'likes_list':likes,
			'date':date_now,
			}
			mongo.db.posts.insert_one(post)
			log_activity(current_user,{'created_new_post':datetime.datetime.now()})
			return redirect(url_for('home'))

@app.route('/posts', methods=['POST','GET'])
@jwt_optional
def posts():
	current_user = get_jwt_identity()
	user_id=None
	if current_user:
		user_id = mongo.db.users.find_one_or_404({'username':current_user})['_id']
		log_activity(current_user,{'viewed_posts':datetime.datetime.now()})
	posts = mongo.db.posts.find().sort('date',-1)
	return render_template('posts.html', user_info=current_user, user_id=user_id, posts=posts)

@app.route('/like', methods=["POST","GET"])
@jwt_required
def like():
	current_user = get_jwt_identity()
	if request.method=="POST":
		user_id = request.form.get('user')
		post_id = request.form.get('post')
		post = mongo.db.posts.find_one_or_404({'_id':ObjectId(request.form.get('post'))})
		likes_dict = post['likes_list']
		print(likes_dict)
		likes_accum = post['likes']
		if request.form.get('like')=='like':
			try:
				date_now = datetime.datetime.now()
				likes_dict.update({user_id:date_now})
				likes_accum += 1
				log_activity(current_user,{'liked_post':{post_id:datetime.datetime.now()}})
				mongo.db.posts.update_one({'_id':ObjectId(post['_id'])},{'$set':{'likes_list':likes_dict,'likes':likes_accum}})
			except Exception as e:
				print(e)
		elif request.form.get('like')=='dislike':			
			try:
				likes_dict.pop(user_id)
				likes_accum -= 1
				log_activity(current_user,{'disliked_post':{post_id:datetime.datetime.now()}})
				mongo.db.posts.update_one({'_id':ObjectId(post['_id'])},{'$set':{'likes_list':likes_dict,'likes':likes_accum}})
			except Exception as e:
				print(e)
	likes_accum = mongo.db.posts.find_one_or_404({'_id':ObjectId(post_id)})['likes']
	return render_template('like.html',likes=likes_accum)

@app.route('/delete', methods=["POST","GET"])
@jwt_required
def delete():
	current_user = get_jwt_identity()
	if request.method=="POST":
		if request.form.get('delete')=="post_by_id":
			post_id = request.form.get('post_id')
			try:			
				filename = mongo.db.posts.find_one_or_404({'_id':ObjectId(post_id)})['photo_name']
				if filename!='0':
					file_id = mongo.db.fs.files.find_one_or_404({'filename':filename})['_id']
					mongo.db.fs.chunks.delete_many({'files_id':file_id})
					mongo.db.fs.files.delete_one({'_id':ObjectId(file_id)})
			except Exception as e:
				print(e)
			log_activity(current_user,{'deleted_post':{post_id:datetime.datetime.now()}})
			mongo.db.posts.delete_one({'_id':ObjectId(post_id)})
	return redirect(url_for('home'))

@app.route('/file/<filename>')
def file(filename):
	print('filename on send ', filename)
	return mongo.send_file(filename)