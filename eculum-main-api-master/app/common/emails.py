from threading import Thread
from flask_mail import Message
import app
from flask import render_template
from app.common.conn_db import db
import jwt
from app.common.config import *

def async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper

@async
def send_async_email(app, msg):
    with app.app.app_context():
        app.mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    send_async_email(app, msg)

def send_email_premium_details(email, data):
    send_email("Premium Request", EMAIL_ADMINS[0], [email],
                render_template("email_premium_details.txt", data=data),
                render_template("email_premium_details.html", data=data))

def send_email_verify(email):
    coll = db['user']
    data  = coll.find_one({"email":email})
    payload = {
                'email': data['email'],
                'secret_key': PRIVATE_KEY
            }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

    send_email("Verify Email", EMAIL_ADMINS[0], [email],
                render_template("email_verify_mail.txt", 
                               user=data['twitter']['name'],
                               token=token.decode()),
                render_template("email_verify_mail.html", 
                                user=data['twitter']['name'], 
                                token=token.decode()))
    