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
import pandas as pd
from datetime import datetime
from app.twitter.words import Keywords


parser = reqparse.RequestParser()
parser.add_argument('username', type=str)
class WordsCount(Resource):
	decorators = [requires_auth]
	def get(self):
		try:
			coll = db['user']
			u = jwt.decode(request.headers['Authorization'], os.environ['SECRET_KEY'])
			user_data = coll.find_one({"_id": ObjectId(u['id'])})
			all_data = {}
			k = Keywords(user_data)
			k.get_tweet_words()
			all_data['hashtags'] = k.get_tags_count()
			coll = db['user_words']
			coll.update_one({'uid': ObjectId(u['id'])}, {'$set': all_data}, upsert=True)

			return Response(json.dumps({'data': all_data}), 200)
		except Exception as e:
			return Response(make_message(str(e)), 400)

	def post(self):
		try:
			args = parser.parse_args()
			username = str(args['username'])
			coll = db['user']
			u = jwt.decode(request.headers['Authorization'], os.environ['SECRET_KEY'])
			data = coll.find_one({"_id": ObjectId(u['id'])})
			auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
			auth.set_access_token(data['twitter']['access_token'], \
								data['twitter']['access_secret_token'])
			k = Keywords(data, username)
			k.get_tweet_words()
			all_data = {}
			all_data['hashtags'] = k.get_tags_count()
			return Response(json.dumps({'data': all_data}), 200)
		except Exception as e:
			return Response(make_message(str(e)), 400)
