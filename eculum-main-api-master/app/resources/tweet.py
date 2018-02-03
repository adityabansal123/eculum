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
parser.add_argument('tweet', type=str)
class Tweet(Resource):
	decorators = [requires_auth]
	def post(self):
		try:
			args = parser.parse_args()
			message = str(args['tweet'])
			coll = db['user']
			u = jwt.decode(request.headers['Authorization'], os.environ['SECRET_KEY'])
			data = coll.find_one({"_id": ObjectId(u['id'])})
			auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
			auth.set_access_token(data['twitter']['access_token'], \
								data['twitter']['access_secret_token'])
			coll = db['tweets']
			api = tweepy.API(auth)
			return_data = api.update_status(message)
			coll.insert_one(return_data._json)
			return Response(make_message('Tweet Sent!'), 200)
		except tweepy.TweepError as e:
			return Response(make_message(str(eval(str(e))[0]['message'])), 400) 
		except Exception as e:
			return Response(make_message(str(e)), 400)
