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
from app.twitter.analytics import TwAnalyseInit

class Overview(Resource):
	decorators = [requires_auth]
	def get(self):
		try:
			coll = db['user']
			u = jwt.decode(request.headers['Authorization'], os.environ['SECRET_KEY'])

			today_date = datetime.strftime(datetime.utcnow(), "%Y-%m-%d")
			data_dates = list(map(lambda x: str(x).split(' ')[0], \
								 pd.date_range(end=today_date, periods=10)))
			all_data = {
				'user_interest': {
					'data': [],
					'label': []
				},
				'growth': {
					'heading': 'Network Dynamics',
					'data': [[0], [0]],
					'labels': [0],
					'label': ['followers count', 'friends count']
				}
			}
			coll = db['user']
			collt = db['twitter_analytics']
			q_data = coll.find_one({"_id": ObjectId(u['id'])})
			twna = TwAnalyseInit(q_data, 50)
			all_data['user_interest']['label'], all_data['user_interest']['data'] = twna.user_interest()
			temp_frg = []
			temp_flg = []
			for d in data_dates:
				tw_data = collt.find_one({'uid': ObjectId(u['id']), 'timestamp': d})
				if tw_data:
					tw_data = tw_data['data']
					temp_frg.append(round(tw_data['followers_growth_rate'], 2))
					temp_flg.append(round(tw_data['friends_growth_rate'], 2))
					all_data['growth']['data'][0].append(tw_data['followers_count'])
					all_data['growth']['data'][1].append(tw_data['friends_count'])
					all_data['growth']['labels'].append(d)

			if temp_flg:
				all_data['avg_followers_growth'] = round(sum(temp_flg) / len(temp_flg), 2)
				all_data['avg_friends_growth'] = round(sum(temp_frg) / len(temp_frg), 2)
			else:
				all_data['avg_followers_growth'] = 0
				all_data['avg_friends_growth'] = 0
			if len(all_data['growth']['data'][0]) == 1:
					twna.run()
					all_data['growth']['data'][0].append(twna.followers_count)
					all_data['growth']['data'][1].append(twna.friends_count)
					all_data['growth']['labels'].append(today_date)

			auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
			auth.set_access_token(q_data['twitter']['access_token'], \
								q_data['twitter']['access_secret_token'])
			api = tweepy.API(auth)
			me = api.me()
			all_data['followers'] = me.followers_count
			all_data['friends'] = me.friends_count
			all_data['likes'] = me.favourites_count
			all_data['tweets'] = me.statuses_count
			return Response(json.dumps({'data': all_data}), 200)
		except Exception as e:
			print(e)
			return Response(make_message(str(e)), 400)


class Followers(Resource):
	decorators = [requires_auth]
	def get(self):
		try:
			coll = db['user']
			collt = db['twitter_analytics']
			u = jwt.decode(request.headers['Authorization'], os.environ['SECRET_KEY'])

			today_date = datetime.strftime(datetime.utcnow(), "%Y-%m-%d")
			data_dates = list(map(lambda x: str(x).split(' ')[0], \
								 pd.date_range(end=today_date, periods=7)))
			all_data = {
				'interest': {'data': [], 'label': []},
				'people': []
			}

			if request.args.get('date'):
				d = request.args.get('date')
			else:
				d = 'recent'

			total_p = 0
			temp_int = {}
			tw_data = collt.find_one({'uid': ObjectId(u['id']), 'timestamp': d})
			if not tw_data and d is 'recent':
				if d is 'recent':
					q_data = coll.find_one({"_id": ObjectId(u['id'])})
					twna = TwAnalyseInit(q_data, 50)
					twna.run()
					tw_data = collt.find_one({'uid': ObjectId(u['id']), 'timestamp': d})
				tw_data = tw_data['data']
				for i in tw_data['followers']:
					temp = {
						'profile_image': i['profile_image_url'],
						'name': i['name'],
						'username': i['screen_name'],
						'bio': i['description'],
						'followers': i['followers_count'],
						'following': i['friends_count'],
						'interests': i['interest'],
						'following_relation': i['following']
					}
					if temp_int.get(i['interest']):
						temp_int[i['interest']]+=1
					else:
						temp_int[i['interest']] = 1
					total_p+=1
					all_data['people'].append(temp)
			elif tw_data:
				if d is 'recent' and tw_data['last_checked'] != today_date:
					q_data = coll.find_one({"_id": ObjectId(u['id'])})
					twna = TwAnalyseInit(q_data, 50)
					twna.run()
				tw_data = tw_data['data']
				for i in tw_data['followers']:
					temp = {
						'profile_image': i['profile_image_url'],
						'name': i['name'],
						'username': i['screen_name'],
						'bio': i['description'],
						'followers': i['followers_count'],
						'following': i['friends_count'],
						'interests': i['interest'],
						'following_relation': i['following']
					}
					if temp_int.get(i['interest']):
						temp_int[i['interest']]+=1
					else:
						temp_int[i['interest']] = 1
					total_p+=1
					all_data['people'].append(temp)

			for i in temp_int:
				all_data['interest']['label'].append(i)
				all_data['interest']['data'].append(round((temp_int[i] / total_p)*100,2))
			return Response(json.dumps({'data': all_data}), 200)
		except Exception as e:
			print(e)
			return Response(make_message(str(e)), 400)

class Friends(Resource):
	decorators = [requires_auth]
	def get(self):
		try:
			coll = db['user']
			collt = db['twitter_analytics']
			u = jwt.decode(request.headers['Authorization'], os.environ['SECRET_KEY'])

			today_date = datetime.strftime(datetime.utcnow(), "%Y-%m-%d")
			data_dates = list(map(lambda x: str(x).split(' ')[0], \
								 pd.date_range(end=today_date, periods=7)))
			all_data = {
				'interest': {'data': [], 'label': []},
				'people': []
			}

			temp_int = {}
			if request.args.get('date'):
				d = request.args.get('date')
			else:
				d = 'recent'

			total_p = 0
			temp_int = {}
			tw_data = collt.find_one({'uid': ObjectId(u['id']), 'timestamp': d})
			if not tw_data and d is 'recent':
				if d is 'recent':
					q_data = coll.find_one({"_id": ObjectId(u['id'])})
					twna = TwAnalyseInit(q_data, 50)
					twna.run()
					tw_data = collt.find_one({'uid': ObjectId(u['id']), 'timestamp': d})
				tw_data = tw_data['data']
				for i in tw_data['friends']:
					temp = {
						'profile_image': i['profile_image_url'],
						'name': i['name'],
						'username': i['screen_name'],
						'bio': i['description'],
						'followers': i['followers_count'],
						'following': i['friends_count'],
						'interests': i['interest']
					}
					if temp_int.get(i['interest']):
						temp_int[i['interest']]+=1
					else:
						temp_int[i['interest']] = 1
					total_p+=1
					all_data['people'].append(temp)
			elif tw_data:
				if d is 'recent' and tw_data['last_checked'] != today_date:
					q_data = coll.find_one({"_id": ObjectId(u['id'])})
					twna = TwAnalyseInit(q_data, 50)
					twna.run()
				tw_data = tw_data['data']
				for i in tw_data['friends']:
					temp = {
						'profile_image': i['profile_image_url'],
						'name': i['name'],
						'username': i['screen_name'],
						'bio': i['description'],
						'followers': i['followers_count'],
						'following': i['friends_count'],
						'interests': i['interest']
					}
					if temp_int.get(i['interest']):
						temp_int[i['interest']]+=1
					else:
						temp_int[i['interest']] = 1
					total_p+=1
					all_data['people'].append(temp)
			for i in temp_int:
				all_data['interest']['label'].append(i)
				all_data['interest']['data'].append(round((temp_int[i] / total_p)*100,2))

			return Response(json.dumps({'data': all_data}), 200)
		except Exception as e:
			print(e)
			return Response(make_message(str(e)), 400)


class Dates(Resource):
	decorators = [requires_auth]
	def get(self):
		try:
			collt = db['twitter_analytics']
			u = jwt.decode(request.headers['Authorization'], os.environ['SECRET_KEY'])
			all_data = {
				'dates': []
			}
			for d in collt.find({'uid': ObjectId(u['id'])}):
				if d['timestamp'] != "recent":
					all_data['dates'].append(d['timestamp'])
			return Response(json.dumps({'data': all_data}), 200)
		except Exception as e:
			print(e)
			return Response(make_message(str(e)), 400)

