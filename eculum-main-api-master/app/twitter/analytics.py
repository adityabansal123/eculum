import tweepy
from datetime import datetime
import time
from app.common.config import *
import pymongo
from bson import ObjectId
import multiprocessing
import firefly

class TwAnalyseInit():
    def __init__(self, user_data, recent):
        self.id = user_data['_id']
        self.screen_name = user_data['twitter']['screen_name']
        self.access_token = user_data['twitter']['access_token']
        self.access_token_secret = user_data['twitter']['access_secret_token']
        self.followers_count = user_data['twitter']['followers_count']
        self.friends_count = user_data['twitter']['friends_count']
        self.auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        self.auth.set_access_token(self.access_token, self.access_token_secret)
        self.recent_count = recent
        client = pymongo.MongoClient(os.environ['DB_STRING'], connect=False)
        self.db = client.get_database()

        self.predict_client = firefly.Client(PREDICT_URL, auth_token='cortexai')

        try:
            self.api = tweepy.API(self.auth)
            self.me = self.api.me()
            self.analysed_data = {"followers":[], "friends":[]}
            self.start_time = time.time()
        except Exception as e:
            print(e)

    def user_interest(self):
        total_tweets = 80
        categories_dict = {}
        statuses = self.api.user_timeline(self.screen_name, count=total_tweets)
        for status in statuses:
            temp = self.predict_client.predict(payload=[status.text])[status.text]
            if categories_dict.get(temp):
                categories_dict[temp]+=1
            else:
                categories_dict[temp] = 1
        return [[i for i in categories_dict.keys()], \
                [j for j in categories_dict.values()]]

    def followers_init(self):
        self.new_followers = list()
        for page in tweepy.Cursor(self.api.followers).items(self.recent_count):
            self.new_followers.append(page)

    def friends_init(self):
        self.new_friends = list()
        for page in tweepy.Cursor(self.api.friends).items(self.recent_count):
            self.new_friends.append(page)

    def analyse(self):
        followers_growth_rate = 0
        friends_growth_rate = 0

        for i in self.new_followers:
            st = ''
            if i._json['statuses_count'] and i._json.get('status'):
                st = i._json['status']['text']
            payload = i._json['description'] + st
            if len(payload) > 5:
                i._json['interest'] = self.predict_client.predict(payload=[payload])[payload]
                self.analysed_data['followers'].append(i._json)

        for i in self.new_friends: 
            st = ''
            if i._json['statuses_count'] and i._json.get('status'):
                st = i._json['status']['text']
            payload = i._json['description'] + st
            if len(payload) > 5:
                i._json['interest'] =  self.predict_client.predict(payload=[payload])[payload]
                self.analysed_data['friends'].append(i._json)


        self.analysed_data['followers_growth_rate'] = followers_growth_rate
        self.analysed_data['friends_growth_rate'] = friends_growth_rate
        self.analysed_data['followers_count'] = self.followers_count
        self.analysed_data['friends_count'] = self.friends_count


    def save_data(self):
        timestamp = datetime.strftime(datetime.utcnow(), "%Y-%m-%d")
        time_taken = round(time.time() - self.start_time, 2)
        coll = self.db['twitter_analytics']
        coll.update({'uid': self.id, 'timestamp': 'recent'}, {'$set' : {'data': self.analysed_data, 'last_checked': timestamp}}, upsert=True)

    def run(self):
        self.followers_init()
        self.friends_init()
        self.analyse()
        self.save_data()

