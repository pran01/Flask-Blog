from Flask_Blog.flaskblog import db,login_manager, app
from datetime import datetime
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

class Users(UserMixin,db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(100), nullable=False, unique=True)
    email=db.Column(db.String(50), nullable=False, unique=True)
    passwd=db.Column(db.String(20), nullable=False)
    posts=db.relationship('Blogs',backref='author',lazy=True)

    def get_reset_token(self,expires_sec=1800):
        s=Serializer(app.config['SECRET_KEY'],expires_sec)
        return s.dumps({'user_id':self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s=Serializer(app.config['SECRET_KEY'])
        try:
            user_id=s.loads(token)['user_id']
        except:
            return None
        return Users.query.get(user_id)


    def __repr__(self):
        return "User('{}','{}','{}')".format(self.id,self.name,self.email)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


class Blogs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(100),nullable=False)
    blog=db.Column(db.Text, nullable=False)
    date_created=db.Column(db.DateTime, default=datetime.now)
    user_id=db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)

    def __repr__(self):
        return "post('{}','{}','{}','{}')".format(self.title, self.blog, self.date_created, self.user_id)