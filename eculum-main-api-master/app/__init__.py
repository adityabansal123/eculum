import sys
import os
from flask import Flask, url_for
from flask_mail import Mail
from flask_restful import Api
from app.resources.user import User, UserPassword, UserEmail
from app.resources.auth import TwitterAuth, JWT, EmailAuth,  InstagramAuth
from app.resources.callback import TwitterCallback, EmailCallback, InstagramCallback
from app.resources.tweet import Tweet
from app.resources.verify import EmailVerify
from app.resources.predict import PredictHashtag
from app.common.config import *
from flask_cors import CORS
from app.resources.trends import TrendsAvailable
from app.resources.trends import TrendsPlace, TrendsWorldwide
from app.resources.tw_analytics import Overview, Followers, Friends
from app.resources.auth import AuthValidate
from app.resources.tw_analytics import Dates
from app.resources.tw_words import WordsCount
from app.resources.tw_media import TwMedia
from app.resources.relationship import Follow, Unfollow, UpdateFriendship
from app.resources.tw_user import TwUser
from app.resources.user import Premium
from app.resources.tw_suggestions import RelatedPost
from app.resources.tw_suggestions import SuggReading

app = Flask(__name__)
api = Api(app, prefix="/v1")
cors = CORS(app, resources={r"/*": {"origins": "*"}})

app.config['MAIL_SERVER'] = MAIL_SERVER
app.config['MAIL_PORT'] = MAIL_PORT
app.config['MAIL_USE_TLS'] = MAIL_USE_TLS
app.config['MAIL_USE_SSL'] = MAIL_USE_SSL
app.config['MAIL_USERNAME'] = MAIL_USERNAME
app.config['MAIL_PASSWORD'] = MAIL_PASSWORD

mail = Mail(app)

app.secret_key = os.environ['SECRET_KEY']

api.add_resource(JWT, '/auth/token')
api.add_resource(TwitterAuth, '/auth/twitter')
api.add_resource(InstagramAuth, '/auth/instagram')
api.add_resource(EmailAuth, '/auth/email')
api.add_resource(TwitterCallback, '/callback/twitter')
api.add_resource(InstagramCallback, '/callback/instagram')
api.add_resource(EmailCallback, '/callback/email')
api.add_resource(User, '/user')
api.add_resource(UserPassword, '/user/password')
api.add_resource(UserEmail, '/user/email')
api.add_resource(Tweet, '/tweet')
api.add_resource(EmailVerify, '/verify/email/<token>')
api.add_resource(PredictHashtag, '/predict/hashtag')
api.add_resource(TrendsAvailable, '/trends/available')
api.add_resource(TrendsPlace, '/trends/place')
api.add_resource(TrendsWorldwide, '/trends/worldwide')
api.add_resource(Overview, '/twitter/insights')
api.add_resource(Followers, '/twitter/insights/followers')
api.add_resource(Friends, '/twitter/insights/friends')
api.add_resource(AuthValidate, '/auth/validate')
api.add_resource(Dates, '/twitter/insights/dates')
api.add_resource(WordsCount, '/twitter/insights/words')
api.add_resource(TwMedia, '/twitter/media')
api.add_resource(Follow, '/twitter/relationship/create')
api.add_resource(Unfollow, '/twitter/relationship/destroy')
api.add_resource(UpdateFriendship, '/twitter/relationship/update')
api.add_resource(TwUser, '/twitter/user')
api.add_resource(Premium, '/user/premium/request')
api.add_resource(RelatedPost, '/twitter/suggestions/posts')
api.add_resource(SuggReading, '/twitter/suggestions/reading')
