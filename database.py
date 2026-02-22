"""
This module performs database operations for user login and posts retrieval.
"""
from flask_login import UserMixin
from bson.objectid import ObjectId

class User(UserMixin):
    """
    User class for Flask-Login integration. Each user has the following attributes.
    """
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data['username']
        # self.password = user_data['password']
        # We don't store password field in the database into the User object for security reasons.
        self.email = user_data['email']
        self.liked_posts = user_data.get('liked_posts', [])
        self.sent_posts = user_data.get('sent_posts', [])

def get_user_by_username(db, username):
    """
    Retrieve user from the 'users' collection by username.
    """
    return db.users.find_one({"username": username})

def get_user_by_id(db, user_id):
    """
    Retrieve user from the 'users' collection by user_id.
    """
    return db.users.find_one({"_id": ObjectId(user_id)})
