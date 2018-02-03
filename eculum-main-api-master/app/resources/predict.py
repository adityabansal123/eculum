import os
import jwt
import json
from bson import json_util, ObjectId
from app.common.config import PREDICT_URL
from app.common.util import make_message
from app.resources.auth import requires_auth, SECRET_KEY
from flask import Flask, request, Response
from flask_restful import (Resource, 
							fields, 
							marshal, 
							reqparse)
import firefly

# Post Requests
parser = reqparse.RequestParser()
parser.add_argument('tweet', type=str)
class PredictHashtag(Resource):
	decorators = [requires_auth]
	def __init__(self):
		self.client = firefly.Client(PREDICT_URL, auth_token="cortexai")
	def post(self):
		try:
			args = parser.parse_args()
			message = str(args['tweet'])
			if args['tweet']:
				data = self.client.hashtag(payload=message)
				return Response(json.dumps(data), 200)
			return Response(json.dumps({'words':[], 'hashtags':[]}), 200)
		except Exception as e:
			return Response(make_message(str(e)), 400)
