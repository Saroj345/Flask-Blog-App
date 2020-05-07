from flask import Flask,render_template,request,session,redirect
from flask_sqlalchemy import SQLAlchemy
#from flask_mail import Mail
import json
import os
import math
from datetime import datetime

# MYSQL DB is not supporting directly so importing PYMYSQL Library as MYSQLDB
import pymysql
pymysql.install_as_MySQLdb()

with open('config.json','r') as e:
    params=json.load(e)["params"]

local_server=True


# Database Conncetor and initializing app From FLASK CLASS
app=Flask(__name__)
app.secret_key = 'super secret key'

#Configuring with gmail API
'''app.config.update(
    MAIL_SERVER="smtp.gmail.com",
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USE_TLS=False,
    MAIL_USERNAME=params["gmail_username"],
    MAIL_PASSWORD=params["gmail_pass"]
)
mail=Mail(app)'''

if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params["local_uri"]
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params["prod_uri"]

db=SQLAlchemy(app)

# Class For Creating a database and initalizing it
class Contacts(db.Model):
    '''
    sno,name,email,phone_num,msg,date
    '''
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12),nullable=True)

class Posts(db.Model):
    '''
    sno,title,slug,content,date
    '''
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    subtitle = db.Column(db.String(50), nullable=False)
    slug = db.Column(db.String(25), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12),nullable=True)
    img_file = db.Column(db.String(12),nullable=True)
#Route for homepage
@app.route("/")
def home():
    posts=Posts.query.filter_by().all()
    last=math.ceil(len(posts)/int(params['numberof_post']))
    page=request.args.get('page')
    if(not str(page).isnumeric()):
        page=1
    page=int(page)
    posts=posts[(page-1)*int(params['numberof_post']):(page-1)*int(params['numberof_post'])+int(params['numberof_post'])]
    if(page==1):
        prev="#"
        next="/?page="+str(page+1)
    elif(page==last):
        prev="/?page="+str(page-1)
        next="#"
    else:
        prev="/?page="+str(page-1)
        next="/?page="+str(page-1)

    #posts=Posts.query.filter_by().all() [0:params['numberof_post']]
    return render_template("index.html",params=params,posts=posts,prev=prev,next=next)

#Route for About Page
@app.route("/about")
def about():
    return render_template("about.html",params=params)

#Route for dashboard
@app.route("/dashboard",methods=['GET','POST'])
def dashboard():
    if 'user'in session and session['user']==params['admin_user']:
        posts = Posts.query.all()
        return render_template('dashboard.html',params=params,posts=posts)
    if request.method == 'POST':
        uname=request.form.get('username')
        pswrd=request.form.get('password')
        if(uname==params['admin_user'] and pswrd==params['admin_pass']):
            session['user'] = uname
            posts=Posts.query.all()
            return render_template('dashboard.html',params=params,posts=posts)
    #redirect to admin page

    return render_template("login.html",params=params)

@app.route("/logout")
def logout():
    session.pop("user")
    return redirect("/dashboard")

@app.route("/delete/<string:sno>",methods=['GET','POST'])
def delete(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        post=Posts.query.filter_by(sno = sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect("/dashboard")


#Route for Post Page
@app.route("/post/<string:post_slug>",methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()

    return render_template("post.html",params=params,post=post)

@app.route("/edit/<string:sno>",methods=['GET', 'POST'])
def edit(sno):
    if ('user' in session and session['user']==params['admin_user']):
        if request.method=="POST":
            box_title=request.form.get('title')
            subtitle=request.form.get('subtitle')
            slug=request.form.get('slug')
            content=request.form.get('content')
            img_file=request.form.get('img_file')
            date=datetime.now()
            if sno =='0':
                post=Posts(title=box_title,subtitle=subtitle,slug=slug,content=content,img_file=img_file,date=date)
                db.session.add(post)
                db.session.commit()
            else:
                post=Posts.query.filter_by(sno=sno).first()
                post.title=box_title
                post.subtitle=subtitle
                post.slug=slug
                post.content=content
                post.img_file=img_file
                post.date=date
                db.session.commit()
                return redirect('/edit/'+sno)
        post = Posts.query.filter_by(sno=sno).first()
    return render_template("edit.html",params=params,post=post,sno=sno)

#Route for contactpage
@app.route("/contact",methods=['GET', 'POST'])
def contact():
    if(request.method=="POST"):
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message= request.form.get('message')

        entry = Contacts(name=name, email=email, phone_num=phone, msg=message, date=datetime.now())
        db.session.add(entry)
        db.session.commit()
        '''mail.send_message('New Message From' + name,
                          sender=email,
                          recipients=[params['gmail_username']],
                          body=message + "\n" + phone
                          )'''
    return render_template("contact.html",params=params)


app.run(debug=True)
