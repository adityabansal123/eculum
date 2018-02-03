import json
import tweepy
from datetime import datetime
from app.common.config import *
from app.common.conn_db import *
from bson import json_util, ObjectId
from app.common.util import make_message, exchange_code_for_ig_access_token 
from app.common.util import render_error_template
from flask_restful import Resource, reqparse
from flask import (request, 
					redirect, 
					session, 
					jsonify, 
					Response, 
					render_template)
import app.common.emails as eml
from instagram.client import InstagramAPI
import pyotp
import jwt
import hashlib

class TwitterCallback(Resource):
	def get(self):
		try:
			verifier = request.args['oauth_verifier']
			token = session.pop('request_token')
			auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, callback_url)
			auth.request_token = token
			auth.get_access_token(verifier)
			api = tweepy.API(auth)
			me  = api.me()
			tw_id = me.id_str
			coll = db['user']
			data = {
				"premium": 0,
				"twitter": {
					"id": tw_id,
					"screen_name": me.screen_name,
					"name": me.name,
					"location": me.location,
					"verified": me.verified,
					"followers_count": me.followers_count,
					"friends_count": me.friends_count,
					"access_token": auth.access_token, 
					"access_secret_token": auth.access_token_secret,
					"profile_image": me.profile_image_url_https
				}
			}
			user = coll.find_one({"twitter.id" : tw_id})
			if user and (user.get('email') or user.get('password')):
				coll.update_one({"twitter.id": tw_id}, \
								{"$set": {"twitter": data['twitter']}})
				totp = pyotp.TOTP('base32secret3232')
				payload = {
					'access_token': data['twitter']['access_token'],
					'otp': totp.now()
				}
				login_hash = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
				# redirect to get_token page
				return redirect('{}/waiting?token={}'.format(os.environ['CLIENT_URL'], login_hash.decode()))
			else:
				data['email_verified'] = False
				data['joined_on'] = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
				if not user:
					coll.insert_one(data)
				session['login_hash'] = data['twitter']['access_token']
				return redirect('{}/register?token={}'.format(os.environ['CLIENT_URL'], 
														data['twitter']['access_token']))
		except Exception as e:
			#redirect to error page
			return render_error_template("Twitter Auth failed, Try Again")

class InstagramCallback(Resource):
	def get(self):
		try:
			api = InstagramAPI(**instaConfig)
			code = request.args.get('code')
			data = exchange_code_for_ig_access_token(api, code)
			return data
		except Exception as e:
			return render_error_template("Cannot get Instagram Auth Token, Try Again")


parser = reqparse.RequestParser()
parser.add_argument('email', type=str)
parser.add_argument('password', type=str)
parser.add_argument('register_token', type=str)
class EmailCallback(Resource):
	def post(self):
		try:
			args = parser.parse_args()
			email = str(args['email'])
			pswd = str(args['password'])
			pswd = hashlib.md5(pswd.encode()).hexdigest()
			access_token = str(args['register_token'])
			coll = db['user']
			if coll.find_one({"email":email}):
				raise Exception("Email already taken")
			if len(pswd) < 8:
				raise Exception("Password is too small")
			if coll.update_one({"twitter.access_token": access_token}, \
							{"$set":{"email": email, "password":pswd}}).matched_count:
				eml.send_email_verify(email)
				totp = pyotp.TOTP('base32secret3232')
				payload = {
					'access_token': access_token,
					'otp': totp.now()
				}
				login_hash = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
				return Response(json.dumps({"message":"Success!", 
											"next":"/waiting?token={}".format(login_hash.decode())}), 200)
			else:
				raise Exception("Error, Please try again!")
		except Exception as e:
			return Response(make_message(str(e)), 401)
