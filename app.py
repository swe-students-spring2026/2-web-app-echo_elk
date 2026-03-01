"""
the app.py file is the main entry point for the Flask application. 
It sets up the Flask app, connects to MongoDB, 
and defines the route for each of all 6 screens,
user authentication, and database interaction.
"""
import os
import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from bson.objectid import ObjectId
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

@app.route('/', methods = ['GET'])
@login_required
def home():
    """
    Fetch all posts from MongoDB.
    """
    # TODO: Perhaps support search query like
    # "title:Foo author:Foo Barstein", etc.
    query = request.args.get('query', '')
    books = list(db.posts.find({
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"author": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
                {"lender_name": {"$regex": query, "$options": "i"}}
            ]
        }))
    return render_template('home.html', books = books, enteredQuery = query)

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    """
    Displays the user's account information.
    Allows the user to update their email address.
    Has a logout button that ends the session and redirects to the login page.
    """
    if request.method == 'POST':
        new_email = request.form.get('email')
        # Update the email in MongoDB
        db.users.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$set": {"email": new_email}}
        )
        flash("Account updated successfully!", "success")
        return redirect(url_for('account'))

    # For GET requests, we need to fetch the actual post details
    # for the IDs stored in liked_posts and sent_posts
    liked_books = list(db.posts.find({"_id": {"$in": current_user.liked_posts}}))
    sent_books = list(db.posts.find({"_id": {"$in": current_user.sent_posts}}))

    return render_template('account.html',
                           liked_books=liked_books,
                           sent_books=sent_books)

@app.route('/delete-post/<post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    """
    Deletes a book post in each user's account page.
    Removes the post ID from the user's 'sent_posts' list and from all users' 'liked_posts' lists.
    We don't handle deleting this book's ID for any user that liked this book. 
    That would be handled when we fetch the posts for the 'liked_posts' list in the account page,
    when a specific user enters their account page.
    """
    p_id = ObjectId(post_id)
    user_id = ObjectId(current_user.id)

    post = db.posts.find_one({"_id": p_id, "lender_id": str(user_id)})
    if not post:
        # 403 means the server does not allow this action. 
        # This should never happen because the delete button should only show for the lender, 
        # but good to have just in case.
        return {"error": "Can't find this post or it's sender!"}, 403
    # Remove this post's ID from this user's 'sent_posts' field.
    db.users.update_one({"_id": user_id}, {"$pull": {"sent_posts": p_id}})
    # Remove this post's ID from the posts collection.
    db.posts.delete_one({"_id": p_id})

    # Clean up other users' liked lists. But this would be slow if many users.
    # So we implement another way. See the docstring above for details.
    # db.users.update_many({"liked_posts": p_id}, {"$pull": {"liked_posts": p_id}})
    flash("Post successfully deleted!", "success")
    return redirect(url_for('account'))

@app.route('/create-post', methods=['GET', 'POST'])
@login_required
def create_post():
    """
    Create a new book post.
    Links the new post ID to the user's 'sent_post' list.
    """
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        description = request.form.get('description') # create more fields later.
        new_post = {
            "title": title,
            "author": author,
            "description": description,
            "lender_id": current_user.id, 
            "lender_name": current_user.username,
            'num_ppl_wanted': 0,
            "created_at": datetime.datetime.now(datetime.timezone.utc)
        }
        current_post = db.posts.insert_one(new_post)
        current_post_id = current_post.inserted_id
        # Update the current_user's 'sent_post' list with the ID of this new post.
        # $push adds the ID to the array without overwriting existing ones
        db.users.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$push": {"sent_posts": current_post_id}}
        )
        # 'flash' is a bit of an annoying way to show a message.
        # try to find another way that does not stop the flow of interaction.
        flash("Book posted successfully!")
        return redirect(url_for('home'))
    return render_template('create_post.html')

@app.route('/like-book/<book_id>', methods=['POST'])
@login_required
def like_book(book_id):
    """
    When a user clicks the 'Like' button on a book post, this route is triggered.
    Find the book and increment the 'num_ppl_wanted' field by 1.
    """
    user_id = ObjectId(current_user.id)
    bk_id = ObjectId(book_id)

    current_bk = db.posts.find_one({"_id": bk_id})
    # Check if this book is in the user's 'sent_posts' list.
    # If yes, they are the lender, and they shouldn't be able to like their own book.
    if str(current_bk.get('lender_id')) == str(current_user.id):
        return {"error": "Are you trying to like your own post? LOL"}, 400
    # Check if the user has already liked this book.
    # Because, reasonably, a user should only like a book once.
    user = db.users.find_one({"_id": user_id, "liked_posts": bk_id})
    if user:
        return {"error": "You have already liked this book."}, 400
    # If first time liking, add the book ID to the user's 'liked_posts' list.
    db.users.update_one(
        {"_id": user_id},
        {"$push": {"liked_posts": bk_id}}
    )

    # increment the book's 'num_ppl_wanted' count.
    result = db.posts.find_one_and_update(
        {"_id": ObjectId(book_id)},
        {"$inc": {"num_ppl_wanted": 1}},
        return_document=True
    )
    if result:
        return {"new_count": result.get('num_ppl_wanted', 0)}, 200
    return {"error": "Book not found"}, 404 # Should never happen, but good to have.

@app.route('/book/<book_id>')
@login_required
def book_details(book_id):
    """
    Displays detailed data for this book.
    """
    book = db.posts.find_one({"_id": ObjectId(book_id)})
    if not book:
        flash("Book not found!", "error")
        return redirect(url_for('home'))
    return render_template('book_details.html', book=book)

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
