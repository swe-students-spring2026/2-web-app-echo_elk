"""
the app.py file is the main entry point for the Flask application. 
It sets up the Flask app, connects to MongoDB, 
and defines the route for each of all 6 screens,
user authentication, and database interaction.
"""
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from bson.objectid import ObjectId
import datetime
from pymongo import MongoClient

# Import the custom database module we wrote
# To separate it from the db in the mongo client, we name it dbm (database module)
import database as dbm

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")

# For mongodb database operations
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DBNAME")]

# Initialize Flask-Login for session management
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirects unauthorized users here

@login_manager.user_loader
def load_user(user_id):
    """
    This function is a bit confusing to understand, so necessary to explain in detail:
    When a user logs in, Flask-Login encryptes the unique ID 
        and saves it in the cookie in the user's browser.
    Every time the user clicks a link to a new page (like 'Home' or 'My Account'), 
        the browser sends that ID back to the server.
    Flask-Login automatically calls THIS function and hands it that ID.
    This function looks up that ID in our MongoDB 'users' collection.
    If found, it returns a 'User' object. This is what allows you to use 
    'current_user.username' in your HTML templates.
    """
    user_data = dbm.get_user_by_id(db, user_id)
    if user_data:
        return dbm.User(user_data)
    return None

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Allows new users to create an account by hashing their password and 
    storing their data in the MongoDB 'users' collection.
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Check if user already exists to avoid duplicates.
        # If yes, redirect back and give another chance.
        if db.users.find_one({"username": username}):
            flash('Username already exists. Pick a different one!')
            return redirect(url_for('register'))
        # Hash the password for security
        hashed_password = generate_password_hash(password)
        # Create the user document based on the user schema.
        # Create more fields later! e.g. email, liked_posts, sent_posts.
        # Note that we should store post IDs.
        new_user = {
            "username": username,
            "password": hashed_password,
            "email": "",  # We can add email field later when we implement the account page.
            "liked_posts": [],
            "sent_posts": []
        }
        db.users.insert_one(new_user)
        flash('Account created! Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login. On GET, show the login form. 
    On POST, validate credentials and log the user in, then starts a session. 
    If credentials are invalid, show an error message.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_data = dbm.get_user_by_username(db, username)
        if user_data and check_password_hash(user_data['password'], password):
            user = dbm.User(user_data)
            login_user(user)
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')

@app.route('/')
@login_required
def home():
    """
    Fetch all posts from MongoDB.
    """
    # Need to implement search bar later here.
    books = list(db.posts.find())
    return render_template('home.html', books=books)

@app.route('/book/<book_id>')
@login_required
def book_details(book_id):
    """
    Displays detailed data for this book.
    """
    # logic for fetching single book would go here
    return render_template('book_details.html')

@app.route('/account')
@login_required
def account():
    """
    Displays the user's account information.
    Displays the user's username, email, a list of their liked posts, and a list of their sent posts.
    And a logout button that ends the session and redirects to the login page.
    """
    return render_template('account.html')

@app.route('/logout')
@login_required
def logout():
    """
    Ends the user session and clears the browser's session cookie.
    """
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
