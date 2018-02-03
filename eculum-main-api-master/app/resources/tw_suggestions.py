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
from app.twitter.words import Keywords
import pandas as pd
from datetime import datetime

class RelatedPost(Resource):
	decorators = [requires_auth]
	def get(self):
		try:
			coll = db['user']
			u = jwt.decode(request.headers['Authorization'], os.environ['SECRET_KEY'])
			user_data = coll.find_one({"_id": ObjectId(u['id'])})
			tweets = []
			kw = Keywords(user_data, count=50)
			kw.get_tweet_words()
			words = kw.get_tags_count()
			words = sorted(words.items(), key=lambda value: value[1], reverse=True)[:10]
			api = twitter_api(user_data)
			for i in words:
				for t in api.search(q=i[0], rpp=i[1], lang='en'):
					t._json['eclm_tag'] = i
					tweets.append(t._json)
			return Response(json.dumps({'data': tweets}), 200)
		except Exception as e:
			return Response(make_message(str(e)), 400)


class SuggReading(Resource):
	decorators = [requires_auth]
	def get(self):
		try:
			coll = db['users_articles']
			return_data = []
			u = jwt.decode(request.headers['Authorization'], os.environ['SECRET_KEY'])
			user_data = coll.find_one({"uid": ObjectId(u['id'])})

			titles = []
			for i in user_data['articles']:
				if i['title'] not in titles:
					return_data.append({
						'keywords': i['keywords'],
						'image': i['image'], 
						'summary': i['summary'],
						'description': i['description'], 
						'title': i['title'],
						'url': i['url']
					})
					titles.append(i['title'])
			return Response(json_util.dumps({'articles': return_data}), 200)
		except Exception as e:
			return Response(make_message(str(e)), 400)
