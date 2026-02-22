"""
the app.py file is the main entry point for the Flask application. 
It sets up the Flask app, connects to MongoDB, 
and defines the route for the home page where it fetches all posts from the database 
and renders them using a template.
"""
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request
from pymongo import MongoClient

load_dotenv() # Loads MONGO_URI from .env

app = Flask(__name__)
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DBNAME")]

@app.route('/')
def home():
    """
    Fetch all posts from MongoDB
    """
    books = list(db.posts.find())
    return render_template('home.html', books=books)

if __name__ == '__main__':
    app.run(debug=True)
