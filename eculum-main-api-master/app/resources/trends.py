import os
import jwt
import json
import tweepy
import json
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


class TrendsAvailable(Resource):
	decorators = [requires_auth]
	def get(self):
		try:
			coll = db['user']
			u = jwt.decode(request.headers['Authorization'], os.environ['SECRET_KEY'])
			data = coll.find_one({"_id": ObjectId(u['id'])})
			auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
			auth.set_access_token(data['twitter']['access_token'], \
								data['twitter']['access_secret_token'])
			api = tweepy.API(auth)
			trends_data = api.trends_available()
			return Response(json.dumps(trends_data), 200)
		except tweepy.TweepError as e:
			return Response(make_message(str(eval(str(e))[0]['message'])), 400) 
		except Exception as e:
			return Response(make_message(str(e)), 400)


parser = reqparse.RequestParser()
parser.add_argument('woeid', type=str)
class TrendsPlace(Resource):
	decorators = [requires_auth]
	def get(self):
		try:
			args = parser.parse_args()
			woeid = str(args['woeid'])
			coll = db['user']
			u = jwt.decode(request.headers['Authorization'], os.environ['SECRET_KEY'])
			data = coll.find_one({"_id": ObjectId(u['id'])})
			auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
			auth.set_access_token(data['twitter']['access_token'], \
								data['twitter']['access_secret_token'])
			api = tweepy.API(auth)
			trends_data = api.trends_place(woeid)
			return Response(json.dumps(trends_data), 200)
		except tweepy.TweepError as e:
			return Response(make_message(str(eval(str(e))[0]['message'])), 400) 
		except Exception as e:
			return Response(make_message(str(e)), 400)


class TrendsWorldwide(Resource):
	decorators = [requires_auth]
	def get(self):
		try:
			coll = db['user']
			u = jwt.decode(request.headers['Authorization'], os.environ['SECRET_KEY'])
			data = coll.find_one({"_id": ObjectId(u['id'])})
			auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
			auth.set_access_token(data['twitter']['access_token'], \
								data['twitter']['access_secret_token'])
			api = tweepy.API(auth)
			trends_data = api.trends_place('1')
			trends_data = trends_data[0]['trends']
			return Response(json.dumps(trends_data[:7]), 200)
		except tweepy.TweepError as e:
			return Response(make_message(str(eval(str(e))[0]['message'])), 400) 
		except Exception as e:
			return Response(make_message(str(e)), 400)