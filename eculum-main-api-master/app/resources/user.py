import os
import jwt
import json
from app.common.conn_db import *
from bson import json_util, ObjectId
import app.common.util as util
from app.resources.auth import requires_auth, SECRET_KEY
from flask import Flask, request, Response
from flask_restful import (Resource, 
							fields, 
							marshal, 
							reqparse)
import app.common.emails as eml
import hashlib
from app.common.util import get_date


#GET Requests
twitter = {}
twitter['id'] = fields.String()
twitter['location'] = fields.String()
twitter['screen_name'] = fields.String()
twitter['name'] = fields.String()
twitter['profile_image'] = fields.String()
resource_fields = {}
resource_fields['uid'] = fields.String(attribute="_id")
resource_fields['twitter'] = fields.Nested(twitter)
resource_fields['email'] = fields.String()
resource_fields['premium'] = fields.String()


class User(Resource):
	decorators = [requires_auth]
	def get(self):
		coll = db['user']
		u = jwt.decode(request.headers['Authorization'], os.environ['SECRET_KEY'])
		data = coll.find_one({'_id': ObjectId(u['id'])})
		return Response(json_util.dumps(marshal(data, resource_fields)), 200)

parser = reqparse.RequestParser()
parser.add_argument('old_password', type=str)
parser.add_argument('new_password', type=str)
class UserPassword(Resource):
	decorators = [requires_auth]
	def post(self):
		try:
			args = parser.parse_args()
			old_pswd = str(args['old_password'])
			old_pswd = hashlib.md5(old_pswd.encode()).hexdigest()
			new_pswd = str(args['new_password'])
			new_pswd = hashlib.md5(new_pswd.encode()).hexdigest()
			coll = db['user']
			u = jwt.decode(request.headers['Authorization'], os.environ['SECRET_KEY'])
			if len(new_pswd) < 8:
				raise Exception("Password must be atleast 8 characters long")

			if coll.update_one({"email":u['email'],"password":old_pswd}, \
						{"$set":{"password":new_pswd}}).matched_count:

				token = jwt.encode({"email":u['email'], "password":new_pswd, \
									'id': str(u['id'])},
									SECRET_KEY, algorithm='HS256')
				res = {
					"message":"Password updated",
					"token": token.decode()
				}
				return Response(json.dumps(res), 200)
			else:
				raise Exception("Password is incorrect")
		except Exception as e:
			return Response(util.make_message(str(e)), 400)


parser.add_argument('new_email', type=str)
class UserEmail(Resource):
	decorators = [requires_auth]
	def post(self):
		try:
			args = parser.parse_args()
			new_email = str(args['new_email'])
			coll = db['user']
			u = jwt.decode(request.headers['Authorization'], os.environ['SECRET_KEY'])

			if coll.update_one({"email":u['email'],"password":hashlib.md5(u['password'].encode()).hexdigest()}, \
						{"$set":{"email":new_email}}).matched_count:

				token = jwt.encode({"email": new_email, "password":u['password'], \
									'id': str(u['id'])},
									SECRET_KEY, algorithm='HS256')
				eml.send_email_verify(new_email)
				res = {
					"message":"Email updated, Please verify new email",
					"token": token.decode()
				}
				return Response(json.dumps(res), 200)
			else:
				raise Exception("Some error ocurred")
		except Exception as e:
			return Response(util.make_message(str(e)), 400)

			parser.add_argument('new_email', type=str)

parser.add_argument('fname', type=str)
parser.add_argument('lname', type=str)
parser.add_argument('email', type=str)
parser.add_argument('country', type=str)		
class Premium(Resource):
	decorators = [requires_auth]
	def post(self):
		try:
			args = parser.parse_args()
			fname = str(args['fname'])
			lname = str(args['lname'])
			email = str(args['email'])
			country = str(args['country'])
			collu = db['user']
			collp = db['premium']
			u = jwt.decode(request.headers['Authorization'], os.environ['SECRET_KEY'])
			user = collu.find_one({"_id": ObjectId(u['id'])})
			idata = {
				"user_email": user['email'],
				"contact_email": email,
				"first_name": fname,
				"last_name": lname,
				"country": country,
				"screen_name": user['twitter']['screen_name'],
				"date": get_date()
			}
			collp.insert_one(idata)
			eml.send_email_premium_details("mail2paras.s@gmail.com", idata)
			eml.send_email_premium_details("paras@eculum.com", idata)
			eml.send_email_premium_details("bansaladitya209@gmail.com", idata)
			eml.send_email_premium_details("aditya@eculum.com", idata)

			return Response(util.make_message("Request Submitted"), 200) 

		except Exception as e:
			return Response(util.make_message(str(e)), 400)

