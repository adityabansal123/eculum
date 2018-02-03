import os
import jwt
import json
import tweepy
from app.common.config import *
from app.common.conn_db import *
from bson import json_util, ObjectId
from app.common.util import make_message
from app.resources.auth import requires_auth, SECRET_KEY
from flask import Flask, request, Response
from flask_restful import (Resource, 
							fields, 
							marshal, 
							reqparse)

# Post Requests
parser = reqparse.RequestParser()
parser.add_argument('screen_name', type=str)
class TwUser(Resource):
	decorators = [requires_auth]
	def post(self):
		try:
			args = parser.parse_args()
			screen_name = str(args['screen_name'])
			coll = db['user']
			u = jwt.decode(request.headers['Authorization'], os.environ['SECRET_KEY'])
			data = coll.find_one({"_id": ObjectId(u['id'])})
			coll = db['twitter_analytics']
			api = twitter_api(data)
			r = api.get_user(screen_name)
			return Response(json.dumps({'data': r._json}), 200)
		except tweepy.TweepError as e:
			return Response(make_message(str(eval(str(e))[0]['message'])), 400) 
		except Exception as e:
			return Response(make_message(str(e)), 400)

