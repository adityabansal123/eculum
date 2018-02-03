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
import twitter


# Post Requests
parser = reqparse.RequestParser()
parser.add_argument('screen_name', type=str)
class Follow(Resource):
	decorators = [requires_auth]
	def post(self):
		try:
			args = parser.parse_args()
			screen_name = str(args['screen_name'])
			coll = db['user']
			u = jwt.decode(request.headers['Authorization'], os.environ['SECRET_KEY'])
			data = coll.find_one({"_id": ObjectId(u['id'])})
			api = twitter_api(data)
			r = api.create_friendship(screen_name, follow=False)
			return Response(make_message(r._json), 200)
		except tweepy.TweepError as e:
			return Response(make_message(str(eval(str(e))[0]['message'])), 400) 
		except Exception as e:
			return Response(make_message(str(e)), 400)

parser.add_argument('do_follow', type=int)
class UpdateFriendship(Resource):
	decorators = [requires_auth]
	def post(self):
		try:
			args = parser.parse_args()
			screen_name = str(args['screen_name'])
			coll = db['user']
			if args['do_follow']:
				do_follow = True
			else:
				do_follow = False
			u = jwt.decode(request.headers['Authorization'], os.environ['SECRET_KEY'])
			data = coll.find_one({"_id": ObjectId(u['id'])})
			api = twitter.Api(consumer_key=CONSUMER_KEY,
					consumer_secret=CONSUMER_SECRET,
					access_token_key=data['twitter']['access_token'],
					access_token_secret=data['twitter']['access_secret_token'])

			api.UpdateFriendship(screen_name=screen_name, follow=do_follow, device=do_follow)
			return Response(make_message('Success!'), 200)
		except Exception as e:
			return Response(make_message(str(e)), 400)

class Unfollow(Resource):
	decorators = [requires_auth]
	def post(self):
		try:
			args = parser.parse_args()
			screen_name = str(args['screen_name'])
			coll = db['user']
			u = jwt.decode(request.headers['Authorization'], os.environ['SECRET_KEY'])
			data = coll.find_one({"_id": ObjectId(u['id'])})
			api = twitter_api(data)
			api.destroy_friendship(screen_name)
			return Response(make_message('Success!'), 200)
		except tweepy.TweepError as e:
			return Response(make_message(str(eval(str(e))[0]['message'])), 400) 
		except Exception as e:
			return Response(make_message(str(e)), 400)
