from flask import Blueprint, render_template, request, redirect, url_for
from flask_jwt_extended import jwt_required,get_jwt_identity,jwt_optional
import datetime

from application import mongo

from random_string import randomString

profile_bpt = Blueprint('profile_bpt', __name__)

def log_activity(username,activity):
	print(activity)
	try:
		log_activity = mongo.db.users.find_one_or_404({'username':username})['log_activity']
	except:
		log_activity={}
	log_activity.update(activity)
	mongo.db.users.update_one({'username':username},{'$set':{'log_activity':log_activity}})


@profile_bpt.route('/profile/<username>', methods=['POST','GET'])
@jwt_optional
def profile(username):
	current_user = get_jwt_identity()
	errors=[]
	profile = mongo.db.users.find_one_or_404({'username':username})
	if current_user:
		log_activity(current_user,{'viewed_profile':{username:datetime.datetime.now()}})
		if username==current_user and request.method=="POST":
			if request.form.get('profile_upload_photo'):
				if 'new_profile_photo' in request.files:
					filename = [0,0,0]
					file = request.files['new_profile_photo']
					filename = file.filename.split('.')
					filename.append(f"{filename[0]}-{randomString(5)}.{filename[1]}")
					#filename.append(f"{filename[0]}.{filename[1]}")
					file_id = mongo.save_file(filename[2],file)
					print(file_id)
					mongo.db.users.update_one({'username':current_user},{'$set':{'photo_name':filename[2]}})
					#session['user_info'] = mongo.db.users.find_one_or_404({'username':user['username']})
					return redirect(url_for('profile_bpt.profile', username=username))
				else:
					errors.append("Error updating photo")
	return render_template('profile.html',user_info=current_user, profile_data=profile, errors=errors)

@profile_bpt.route('/current_user_photo/<username>')
def current_user_photo(username):
	print("working")
	user = mongo.db.users.find_one_or_404({'username':username})
	print("filename is ",user['photo_name'])
	return mongo.send_file(user['photo_name'])

@profile_bpt.route('/standart_user_photo', methods=["POST","GET"])
@jwt_required
def sup():
	if 'errors' in request.args:
		errors = [request.args['errors']]
	else:
		errors=[]
	current_user = get_jwt_identity()
	if current_user!='admin':
		return (render_template('restricted.html', user_info=current_user),403)
	if request.method=="POST" and 'new_standart_user_photo' in request.files:
		try:
			old_photo = mongo.db.fs.files.find_one_or_404({'filename':'profile_standart.jpeg'})
			mongo.db.fs.files.delete_one({'filename':'profile_standart.jpeg'})
			mongo.db.fs.chunks.delete_many({'files_id':old_photo['_id']})
		except:
			print("No old photo found")
		file = request.files['new_standart_user_photo']
		file_id = mongo.save_file('profile_standart.jpeg',file)
		return redirect(url_for('profile_bpt.sup', errors=[f'Inserted with id {file_id}']))
	return render_template('sup.html', user_info=current_user, errors=errors)