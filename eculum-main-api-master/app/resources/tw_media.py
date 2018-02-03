import os
import jwt
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
import werkzeug
from werkzeug.utils import secure_filename
import twitter
import numpy as np
from io import StringIO

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
	return '.' in filename and \
			filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Post Requests

parser = reqparse.RequestParser()
parser.add_argument('image', type=werkzeug.datastructures.FileStorage, location='files')
class TwMedia(Resource):
	decorators = [requires_auth]
	def post(self):
		try:
			if 'image' not in request.files:
				raise Exception('No file')
			file = request.files['image']
			if file.filename == '':
				raise Exception("No image file")
			if file and allowed_file(file.filename):
				filename = secure_filename(file.filename)
				file.save(os.path.join('temp_images', filename))
			else:
				raise Exception("Invalid File")
			coll = db['user']
			u = jwt.decode(request.headers['Authorization'], os.environ['SECRET_KEY'])
			data = coll.find_one({"_id": ObjectId(u['id'])})
			api = twitter.Api(consumer_key=CONSUMER_KEY, 
						consumer_secret=CONSUMER_SECRET,
						access_token_key=data['twitter']['access_token'],
						access_token_secret=data['twitter']['access_secret_token'])
			r_data = api.UploadMediaSimple(open(os.path.join('temp_images', filename), 'rb'))
			os.remove(os.path.join('temp_images', filename))
			return Response(json.dumps({'media_id': r_data}), 200) 
		except Exception as e:
			return Response(make_message(str(e)), 400)
