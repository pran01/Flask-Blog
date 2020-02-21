from flask import render_template, redirect,url_for,request,flash,abort
from Flask_Blog.flaskblog.forms import RegisterForm,LoginForm,NewBlog,ProfileData,RequestResetForm,ResetPasswordForm
from Flask_Blog.flaskblog.models import Users,Blogs
from Flask_Blog.flaskblog import app,db,mail
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,logout_user,current_user,login_required
from flask_mail import Message

otp=0

@app.route('/',methods=['POST','GET'])
def home():
    blogs=Blogs.query.all()
    return render_template('home.html',blogs=blogs,Blogs=Blogs)


@app.route('/register',methods=['POST','GET'])
def register():
    form=RegisterForm()
    if form.validate_on_submit():
        hashed_password=generate_password_hash(form.password.data, method='sha256')
        new_user=Users(name=form.username.data,email=form.email.data,passwd=hashed_password)
        db.session.add(new_user)
        send_confirmation(new_user)
        flash("An email has been sent to confirm the email.")
        return redirect(url_for('login'))
    else:
        return render_template('register.html',form=form)


@app.route('/confirm_mail/<token>')
def confirm_mail(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user=Users.verify_reset_token(token)
    if not user:
        flash('The token is invalid or expired.','warning')
        return redirect(url_for('register'))
    db.session.commit()
    flash('Registration Completed.')
    return redirect(url_for('login'))



@app.route('/users')
def users():
    users=Users.query.all()
    return render_template('users.html', tasks=users)

@app.route('/login',methods=['POST','GET'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user=Users.query.filter_by(name=form.username.data).first()
        if user:
            if check_password_hash(user.passwd,form.password.data):
                login_user(user)
                next_page=request.args.get('next')
                return redirect(next_page) if next_page else redirect('/')
            else:
                flash('password or username incorrect')
        else:
            flash('password or username incorrect')
    else:
        return render_template('login.html',form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/new_blog',methods=['POST','GET'])
@login_required
def new_blog():
    form=NewBlog()
    if form.validate_on_submit():
        post=Blogs(user_id=current_user.id,title=form.title.data, blog=form.blog.data)
        db.session.add(post)
        db.session.commit()
        return redirect('/')
    else:
        return render_template('new_blog.html',form=form,post_num=int(Blogs.query.count()))


@app.route('/profile',methods=['POST','GET'])
@login_required
def profile():
    return render_template('profile.html')


@app.route('/edit_profile',methods=['POST','GET'])
@login_required
def edit_profile():
    form = ProfileData()
    if form.validate_on_submit():
        current_user.name=form.username.data
        current_user.email=form.email.data
        db.session.commit()
        flash('Updated successfully', 'success')
        return redirect('/profile')
    else:
        form.username.data=current_user.name
        form.email.data=current_user.email
        return render_template('new_profile.html',form=form)

@app.route('/about')
def about():
    return(render_template('about.html'))

@app.route('/myblog')
def myblog():
    blogs=Blogs.query.filter_by(user_id=current_user.id).all()
    return render_template('myblogs.html',blogs=blogs,Blogs=Blogs)

@app.route('/blog/<int:blog_id>')
def blog(blog_id):
    blog=Blogs.query.get_or_404(blog_id)
    return render_template('blog.html',blog=blog,Blogs=Blogs)

@app.route('/blog/<int:blog_id>/update',methods=['GET','POST'])
def update_blog(blog_id):
    blog=Blogs.query.get_or_404(blog_id)
    if blog.author.name!=current_user.name:
        abort(403)
    form = NewBlog()
    if form.validate_on_submit():
        blog.title=form.title.data
        blog.blog=form.blog.data
        db.session.commit()
        flash('Updated successfully', 'success')
        return redirect(url_for('blog',blog_id=blog.id))
    elif request.method=='GET':
        form.title.data = blog.title
        form.blog.data = blog.blog
    return render_template('new_blog.html',form=form)


@app.route('/blog/<int:blog_id>/delete',methods=['GET','POST'])
def delete_blog(blog_id):
    blog=Blogs.query.get_or_404(blog_id)
    if blog.author.name!=current_user.name:
        abort(403)
    db.session.delete(blog)
    db.session.commit()
    flash('Deleted Successfully')
    return redirect(url_for('home'))



def send_confirmation(user):
    token = user.get_reset_token()
    msg = Message('Email Confirmation', sender='noreply@flaskblog.com', recipients=[user.email])
    msg.body = """To confirm your email, click on the link below.
        {}.
        If you have not requested this, then simply ignore this mail.
    """.format(url_for('confirm_mail', token=token, _external=True))
    with app.app_context():
        mail.send(msg)

def send_email(user):
    token=user.get_reset_token()
    msg=Message('Password Reset Confirmation',sender='noreply@flaskblog.com',recipients=[user.email])
    msg.body="""To reset the password of your account click on the link below.
    {}.
    If you have not requested this reset then simply ignore this mail and no changes will be made.
""".format(url_for('reset_password',token=token,_external=True))
    with app.app_context():
        mail.send(msg)



@app.route('/reset_password',methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form=RequestResetForm()
    if form.validate_on_submit():
        user=Users.query.filter_by(email=form.email.data).first()
        send_email(user)
        flash('An email has been sent with the instructions on how to reset your password.')
        return redirect(url_for('login'))
    return render_template('reset_request.html',form=form)


@app.route('/reset_password/<token>',methods=['GET','POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user=Users.verify_reset_token(token)
    if not user:
        flash('The token is invalid or expired.','warning')
        return redirect(url_for(reset_request))
    form=ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password=generate_password_hash(form.password.data, method='sha256')
        user.passwd=hashed_password
        db.session.commit()
        flash('Password updated.')
        return redirect(url_for('login'))
    return render_template('reset_password.html',form=form)


'''@app.route('/otp_submit/<otp>',methods=['POST','GET'])
def otp_submit(otp):
    form=OTPsubmitForm()
    if form.validate_on_submit():
        if check_password_hash(otp,form.otp.data):
            db.session.commit()
            flash('Registration Completed.')
            return redirect(url_for('login'))
        else:
            flash('OTP INCORRECT')
    return render_template('enter_otp.html',form=form)'''