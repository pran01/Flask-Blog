from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired,Length,Email,EqualTo,ValidationError
from Flask_Blog.flaskblog.models import Users
from flask_login import current_user


class RegisterForm(FlaskForm):
    username=StringField('username',validators=[DataRequired(message='username can\'t be empty'),Length(min=5,max=10)])
    email=StringField('email',validators=[Email(message='invalid email')])
    password=PasswordField('password',validators=[DataRequired(message='password cannot be empty'),Length(min=8,max=80)])
    conf_password = PasswordField('confirm password',validators=[DataRequired(message='password cannot be empty'), EqualTo('password')])
    register=SubmitField('Register')
    def validate_username(self,username):
        user=Users.query.filter_by(name=username.data).first()
        if user:
            raise ValidationError('Username Already Exist')

    def validate_email(self,email):
        user=Users.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email Already Exist')


class LoginForm(FlaskForm):
    username=StringField('username',validators=[DataRequired(message='username can\'t be empty'),Length(min=5,max=10)])
    password = PasswordField('password',validators=[DataRequired(message='password cannot be empty'), Length(min=8, max=80)])
    remember = BooleanField('Remember me')
    login=SubmitField('Login')
    def validate_username(self,username):
        user=Users.query.filter_by(name=username.data).first()
        if not user:
            raise ValidationError('Username Does Not exist')


class NewBlog(FlaskForm):
    title=StringField('Title',validators=[DataRequired(),Length(min=5)])
    blog=TextAreaField('Blog',validators=[DataRequired()])
    submit=SubmitField('Submit')


class ProfileData(FlaskForm):
    username = StringField('Username',validators=[DataRequired(), Length(min=5, max=10)])
    email = StringField('Email', validators=[Email()])
    submit=SubmitField('Submit')
    def validate_username(self,username):
        if username.data != current_user.name:
            user=Users.query.filter_by(name=username.data).first()
            if user:
                raise ValidationError('Username Already Exist')
    def validate_email(self,email):
        if email.data != current_user.email:
            user=Users.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email Already Exist')


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[Email()])
    reset = SubmitField('Reset')
    def validate_email(self,email):
        user=Users.query.filter_by(email=email.data).first()
        if not user:
            raise ValidationError('Email is not registered')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password',
                             validators=[DataRequired(message='password cannot be empty'), Length(min=8, max=80)])
    conf_password = PasswordField('confirm password',
                                  validators=[DataRequired(message='password cannot be empty'), EqualTo('password')])
    submit = SubmitField('Submit')


class OTPsubmitForm(FlaskForm):
    otp = StringField('OTP', validators=[Length(min=4,max=4)])
    submit = SubmitField('Submit OTP')