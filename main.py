# Importing Flask class, render template
import smtplib
from flask import Flask, render_template, request, session, redirect
import os
from werkzeug.utils import secure_filename
import math

# Importing flask mail
from flask_mail import Mail, Message

# Importing Date time
from datetime import datetime

# Importing JSON module and opening it
import json
with open('config.json','r') as c:
    params = json.load(c)["params"]

# Importing SQLAlchemy from flask_sqlalchemy
from flask_sqlalchemy import SQLAlchemy

# Creating an instance of Flask Class
app = Flask(__name__)
app.secret_key = 'something-secret'
app.config['UPLOAD_FOLDER'] = params['location']

# Setting up URI for the mysql database
app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']

# Setting up SMTP
def sendEmail(reciever, message):
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.login(params['user_name'], params['user_passwd'])
    server.sendmail("", reciever, message)
    server.close()

# Creating mail instance
mail = Mail(app)

# Creating db object of SQLAlchemy class with the flask app object as the parameter
db = SQLAlchemy(app)

# Configuring the contacts database parameters with the ORM
class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    message = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    date = db.Column(db.DateTime, nullable = True)

# Configuring the posts database parameters with the ORM
class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(40), nullable=False)
    slug = db.Column(db.String(40), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable = True)
    img_file = db.Column(db.String(12), nullable=False)
    tagline = db.Column(db.String(20), nullable=False)

#Using route decorator with the app instance to run a function when "/" url is visited
@app.route("/")
def home():
    posts = Posts.query.filter_by().all()
    last = math.ceil(len(posts)/int(params['no_of_posts']))
    page = request.args.get('page')
    if(not str(page).isnumeric()):
        page = 1
    page = int(page)
    posts = posts[(page-1)*int(params['no_of_posts']):(page-1)*int(params['no_of_posts'])+ int(params['no_of_posts'])]
    if page==1:
        prev = "#"
        next = "/?page="+ str(page+1)
    elif page==last:
        prev = "/?page="+ str(page-1)
        next = "#"
    else:
        prev = "/?page="+ str(page-1)
        next = "/?page="+ str(page+1)
    return render_template('index.html',params=params,posts=posts, prev=prev, next=next)

@app.route("/about")
def about():
    return render_template('about.html',params=params)

@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    if(request.method=='POST'):
        '''Fetch values from <form>'''
        Name = request.form.get('name')
        maill = request.form.get('email')
        phone_num = request.form.get('phone') 
        msg = request.form.get('message')

        # Setting up variables for entry in database(variableNames_from_class = variableNames_from_form)
        entry = Contacts(name=Name,email=maill,phone=phone_num,message=msg,date = datetime.now())

        # Entrying into DB
        db.session.add(entry)
        db.session.commit()

        # Sending Email
        sendEmail(params['receivers],f"New message from {Name}:\n{msg}\n{phone_num}")
    return render_template('contact.html',params=params)

@app.route("/post/<string:post_slug>", methods = ["GET"])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html',params=params, post=post,)

@app.route("/dashboard", methods=['GET','POST'])
def dashboard():
    if('user' in session) and session['user'] == params['admin_user']:
        posts = Posts.query.all()
        return render_template('dashboard.html',params=params, posts=posts)

    if(request.method == "POST"):
        """Fetching values from <form>"""
        userName = request.form.get('username')
        passwd = request.form.get('password')
        # Validating the userName and password
        if(userName == params['admin_user'] and passwd == params['admin_passwd']):
            session['user'] = userName
            posts = Posts.query.all()
            return render_template('dashboard.html',params=params, posts=posts)
        else:
            return render_template('login.html',params=params)
    return render_template('login.html',params=params)

@app.route("/edit/<string:sno>", methods=["GET","POST"])
def editPost(sno):
    if('user' in session) and session['user'] == params['admin_user']:
        if(request.method=="POST"):
            edit_title = request.form.get('title')
            edit_tagline= request.form.get('tagline')
            edit_slug= request.form.get('slug')
            edit_content= request.form.get('content')
            edit_img= request.form.get('img_file')
            edit_date = datetime.now()
        
            if(sno=="0"):
                post = Posts(title=edit_title,tagline=edit_tagline,slug=edit_slug,content=edit_content,img_file=edit_img, date=edit_date)
                db.session.add(post)
                db.session.commit()
            
            else:
                post = Posts.query.filter_by(sno=sno).first()
                post.title = edit_title
                post.slug = edit_slug
                post.tagline = edit_tagline
                post.content = edit_content
                post.img_file = edit_img
                post.date = datetime.now()

                db.session.commit()
                return redirect('/edit/' + sno)

        post = Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html',params=params,post=post,sno=sno)

@app.route("/uploader", methods = ['GET','POST'])
def uploader():
    if('user' in session) and session['user'] == params['admin_user']:
        if(request.method=='POST'):
            f = request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            return redirect('/dashboard')

@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/dashboard')

@app.route("/delete/<string:sno>")
def delete(sno):
    if('user' in session) and session['user'] == params['admin_user']:
        post = Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashboard')

# Running server on localhost
app.run(debug=True)
