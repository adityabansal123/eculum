import tweepy
import json
import jwt
from flask_restful import Resource, reqparse
from datetime import datetime, timedelta
from bson import json_util, ObjectId
from functools import wraps
from app.common.config import *
from app.common.conn_db import *
from app.common.util import make_message, render_error_template
from flask import (Flask, 
					request, 
					redirect, 
					session, 
					url_for, 
					jsonify, 
					Response, 
					render_template)
from instagram.client import InstagramAPI
import pyotp
import hashlib

SECRET_KEY = os.environ['SECRET_KEY']
class TwitterAuth(Resource):
	def get(self):
		try:
			auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, callback_url)
			redirect_url = auth.get_authorization_url()
			session['request_token'] = auth.request_token
			return redirect(redirect_url)
		except Exception as e:
			#load error page
			print(e)
			return render_error_template("Cannot connect to Twitter")


class InstagramAuth(Resource):
	def get(self):
		try:
			api = InstagramAPI(**instaConfig)
			url = api.get_authorize_url(scope=["likes","comments"])
			return redirect(url)
		except:
			#load error page
			return render_error_template("Cannot connect to Instagram")

parser = reqparse.RequestParser()
parser.add_argument('email', type=str)
parser.add_argument('password', type=str)
class EmailAuth(Resource):
	def post(self):
		try:
			args = parser.parse_args()
			email = str(args['email'])
			pswd = str(args['password'])
			pswd = hashlib.md5(pswd.encode()).hexdigest()
			coll = db['user']
			data = coll.find_one({"email": email, "password": pswd})
			if data:
				totp = pyotp.TOTP('base32secret3232')
				payload = {
					'access_token': data['twitter']['access_token'],
					'otp': totp.now()
				}
				login_hash = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
				return Response(json.dumps({"message":"Success!", 
											"next":"/waiting?token={}".format(login_hash.decode())}), 200)
			else:
				raise Exception("Invalid Username or Password")
		except Exception as e:
			return Response(make_message(str(e)), 401)


class JWT(Resource):
	def get(self):
		try:
			totp = pyotp.TOTP('base32secret3232')

			payload = jwt.decode(request.args['login_hash'], SECRET_KEY, algorithm='HS256')
			if not totp.verify(payload['otp']):
				raise Exception("Token Expired")
			access_token = payload['access_token']
			coll = db['user']
			dr = coll.find_one({"twitter.access_token": access_token}, \
								{"email":"email", "password":"password", "_id":"_id.oid"})
			payload = {
				'email': dr['email'],
				'password': dr['password'],
				'id': str(dr['_id'])
			}
			token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
			return jsonify(token=token.decode())
		except Exception as e:
			return Response(make_message("Login Again"), 401)




def requires_auth(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		try:
			auth = request.headers['Authorization']
			if not auth:
				raise Exception("No Auth Token")
			payload = jwt.decode(auth, SECRET_KEY, algorithm='HS256')
			coll = db['user']
			if not payload.get('email'):
				raise Exception(jwt.InvalidTokenError)
			data = coll.find_one({"email":payload['email']})
			if not data['password'] == payload['password']:
				raise Exception(jwt.InvalidTokenError)
		except jwt.ExpiredSignatureError:
			return Response(make_message('Signature expired. Please log in again.'))
		except jwt.InvalidTokenError:
			return Response(make_message('Invalid token. Please log in again.'), 401)
		except Exception as e:
			return Response(make_message('Please, Login in again'), 401)
		return f(*args, **kwargs)
	return decorated



class AuthValidate(Resource):
	decorators = [requires_auth]
	def get(self):
		coll = db['user']
		u = jwt.decode(request.headers['Authorization'], os.environ['SECRET_KEY'])
		data = coll.find_one({'_id': ObjectId(u['id'])})
		return Response(json.dumps({'premium': data['premium'], 'valid': 1}), 200)