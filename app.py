from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
import csv
from sqlalchemy import desc, asc
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from flask_mail import Message
from flask_login import LoginManager, UserMixin
from flask_login import login_user, current_user, logout_user, login_required


import functions

user_type_key = {0:'student',
                 1:'teacher',
                 2:'administrator',
                 3:'developer'}

app = Flask(__name__)
login_manager = LoginManager(app)
login_manager.login_view = 'login' #specify the login route

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///library.db"
db = SQLAlchemy(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255),unique=True)
    name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    image_data = (db.Column(db.LargeBinary))
    email_verification_token = db.Column(db.String(255))
    is_verified = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return self.username

@login_manager.user_loader
def load_user(user):return
    # return User.get(user)

@app.route("/")
def index():
    #if logged in, go to dashboard
    #else go to login
    return render_template('index.html')

@login_manager.user_loader
def load_user(user_id):
    return 1
    # return User.query.get(int(user_id))

@app.route('/login',methods=['GET'])
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html') 

@app.route('/charts')
def charts():
    return render_template('charts.html')

@app.route('/forgot')
def forgot():
    return render_template('forgot-password.html') 

# @app.route('/login')
# def login():
#     return render_template('login.html')

# @app.route('/login')
# def login():
#     return render_template('login.html')

# @app.route('/login')
# def login():
#     return render_template('login.html')

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.secret_key = "super_secret_key"  # Change this to a random, secure key
    app.run(debug=True)