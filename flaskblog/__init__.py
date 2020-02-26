from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
import os

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///blog.db'
app.config['SECRET_KEY']='Shh!ItsSecret'
db= SQLAlchemy(app)
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'
login_manager.login_message_category='info'
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT']=587
app.config['MAIL_USE_TLS']=True
app.config['MAIL_USERNAME']=os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD']=os.environ.get('MAIL_PASSWORD')

mail=Mail(app)

from Flask_Blog.flaskblog import routes
