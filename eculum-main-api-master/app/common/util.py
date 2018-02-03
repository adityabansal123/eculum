import json
import os
import requests
from flask import Response, render_template
from functools import wraps  
import datetime

SECRET_KEY = os.environ['SECRET_KEY']

def make_message(s):
	return json.dumps({"message":str(s)})

def render_error_template(message):
    headers = {'Content-Type': 'text/html'}
    return Response(render_template('error.html', message=message), 400, headers)

def exchange_code_for_ig_access_token(api, code):
    url = u'https://api.instagram.com/oauth/access_token'
    data = {
        u'client_id': api.client_id,
        u'client_secret': api.client_secret,
        u'code': code,
        u'grant_type': u'authorization_code',
        u'redirect_uri': api.redirect_uri
    }
    response = requests.post(url, data=data)
    account_data = json.loads(response.text)
    if account_data.get('code'):
        if account_data['code']==400:
            raise Exception(account_data['error_message'])
    return account_data

def dict_list_reduce(d, key):
    data = []
    for i in d:
        data.append(i[key])
    return data
    
def get_date():
    return datetime.datetime.strftime(datetime.datetime.now(), "%y-%m-%d %H:%M:%S")
