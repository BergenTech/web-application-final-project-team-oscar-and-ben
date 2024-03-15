from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import JSON
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
from calendar import weekday
import json

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

def load_default_schedule():
    with open('static/assets/default_schedule.json', 'r') as file:
        default_schedule = json.load(file)
    return default_schedule

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255),unique=True)
    name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Integer,nullable=False)
    schedule_data = db.Column(JSON, default=load_default_schedule)
    sessions = db.relationship('Session', backref='user', lazy = True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    subject = db.Column(db.String(255))
    tutor = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False) # User's ID number
    email = db.Column(db.String(255), unique=True, nullable=False)
    completed = db.Column(db.Boolean, default = False)

    def __repr__(self):
        return f'{self.start_time} - {self.end_time}'

class StupidIdea(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    monday = db.Column(db.String(256), default = '')
    tuesday = db.Column(db.String(256), default = '')
    wednesday = db.Column(db.String(256), default = '')
    thursday = db.Column(db.String(256), default = '')
    friday = db.Column(db.String(256), default = '')

with app.app_context():
    db.create_all()

# to prevent needing to change all the html file templates
@app.route('/index.html')
def reroute_user():
    return redirect(url_for('index'))

@login_manager.user_loader
def load_user(user):
    return User.get(user)

@app.route('/createDB')
def createDB():
    for _ in range(1,10):
        newThing = StupidIdea()
        db.session.add(newThing)
        db.session.commit()
    return redirect(url_for('index'))

@app.route("/")
def index():
    #if logged in, go to dashboard
    #else go to login
    if not current_user.is_authenticated:return redirect(url_for('login'))

    if current_user.role == 0:
        return render_template('index0.html',username=current_user.username)
    elif current_user.role == 1:
        return render_template('index1.html',username=current_user.username)
    return redirect(url_for('login'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid credentials!","danger")
    return render_template("login.html")

@app.route('/logout',methods=['POST'])
def logout():
    logout_user()
    flash('Logged out!','success')
    return redirect(url_for('login'))

@app.route('/register', methods = ['POST','GET'])
def register():
    if request.method == "POST":
        # Get form data
        name = request.form.get("name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        username = request.form.get("username")
        role = request.form.get('role')
        # Validate form data (add your own validation logic)
        if not (
            name
            and last_name
            and email
            and password
            and confirm_password
            and username
            and role
        ):
        # Handle invalid input
            flash("Please fill in all fields.", "danger")
            return render_template("register.html")
        #handle if existing user
        user = User.query.filter_by(email=email).first()
        if user is not None and email == user.email:
            # Handle password mismatch
            flash("User already exist! Try a different email", "danger")
            return render_template("register.html")
        if password != confirm_password:
            # Handle password mismatch
            flash("Passwords do not match.", "danger")
            return render_template("register.html")

        # Create a new user instance
        new_user = User(
            name=name,
            last_name=last_name,
            email=email,
            username=username,
            role=int(role)
        )
        new_user.set_password(password)

        # Save the new user to the database
        db.session.add(new_user)
        db.session.commit()
        
        flash("Account created successfully! Please check your email to verify.", "success")
        return redirect(url_for('login'))
    return render_template("register.html")


@app.route('/session_manager', methods = ['POST','GET'])
def session_manager():
    #use a 2d list that maps from a dictionary for each day and period, and then access
    users = []
    if request.method == 'POST':
        type = request.form.get('type')
        period = request.form.get('period')
        date = request.form.get('date')
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        year, month, day = (int(i) for i in date.split('-'))
        dayNumber = weekday(year, month, day)
        day = days[dayNumber].lower()
        period_data = StupidIdea.query.get(period)
        if type == '0':
            user = current_user
            data = getattr(period_data, day, 'default   ')
            setattr(period_data, day, data + ' ' + str(user.id))
            db.session.commit()
        elif type == '1':
            data = getattr(period_data, day, '')
            user_ids = data.split(' ')
            for id in user_ids:
                user = User.query.get(id)
                users.append(user)  
        
    return render_template('session_manager.html', users = users[1:])

@app.route('/charts')
def charts():
    return render_template('charts.html')

@app.route('/forgot')
def forgot():
    return render_template('forgot-password.html')

@app.route('/buttons')
def buttons():
    return render_template('buttons.html') 

@app.route('/cards')
def cards():
    return render_template('cards.html') 

@app.route('/forgot-password')
def forgot_password():
    return render_template('forgot-password.html') 

@app.route('/tables')
def tables():
    return render_template('tables.html') 

@app.route('/utilities-animation')
def utilities_animation():
    return render_template('utilities-animation.html') 

@app.route('/utilities-border')
def utilities_border():
    return render_template('utilities-border.html') 

@app.route('/utilities-color')
def utilities_color():
    return render_template('utilities-color.html') 

@app.route('/utilities-other')
def utilities_other():
    return render_template('utilities-other.html') 

# @app.route('/login')
# def login():
#     return render_template('login.html')

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.secret_key = "ben_sucks"  # Change this to a random, secure key
    app.run(debug=True)