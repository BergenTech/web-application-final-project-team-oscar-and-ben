
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



app = Flask(__name__)
login_manager = LoginManager(app)
login_manager.login_view = 'login' #specify the login route

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///library.db"
db = SQLAlchemy(app)

@login_manager.user_loader
def load_user(user):
    return User.get(user)

class User(db.Model, UserMixin):
   id = db.Column(db.Integer, primary_key=True)
   name = db.Column(db.String(255))
   last_name = db.Column(db.String(255))
   email = db.Column(db.String(255), unique=True, nullable=False)
   password_hash = db.Column(db.String(255), nullable=False)
   image_data = (db.Column(db.LargeBinary))
   email_verification_token = db.Column(db.String(255))
   is_verified = db.Column(db.Boolean, default=False)
   def __repr__(self):
        return self.username

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')


if __name__ == "__main__":
    app.secret_key = "super_secret_key"  # Change this to a random, secure key
    app.run(debug=True)