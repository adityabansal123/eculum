from flask_restful import Resource
from flask import Response, jsonify, make_response
import jwt
import app.common.util as util
from  app.common.conn_db import *
from app.common.config import SECRET_KEY, PRIVATE_KEY
from flask import render_template

class EmailVerify(Resource):
	def get(self, token):
		try:
			token = jwt.decode(token, SECRET_KEY)
			if token['secret_key'] == PRIVATE_KEY:
				coll = db['user']
				coll.update_one({"email":token['email']}, {"$set":{"email_verified":True}})                                               
				response = make_response(render_template("email_verified.html", 
								message="Email successfully verified"))                                         
				response.headers['Content-Type'] = 'text/html; charset=utf-8'            
				return response
			else:
				raise Exception("Some Error Occurred")
		except:
			response = make_response(render_template("email_verified.html", 
							message="Verification Failed"))                                         
			response.headers['Content-Type'] = 'text/html; charset=utf-8'            
			return response
