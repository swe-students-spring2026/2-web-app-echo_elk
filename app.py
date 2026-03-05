"""
the app.py file is the main entry point for the Flask application. 
It sets up the Flask app, connects to MongoDB, 
and defines the route for each of all 6 screens,
user authentication, and database interaction.
"""
import os
import datetime
from uuid import uuid4 as uuid_uuid4
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
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

# Configuration for local uploads
# Switch to Cloudinary later for storing uploaded images.
UPLOAD_FOLDER = 'static/seed_post_imgs'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Global variables
VALID_SEARCH_FIELDS = ['title', 'author', 'sender_name', 'other_info']

def allowed_file(filename):
    """
    Helper function, check if filename has allowed extension.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        if dbm.get_user_by_username(db, username):
            flash('Username already exists. Pick a different one!')
            return redirect(url_for('register'))
        # Hash the password for security
        hashed_password = generate_password_hash(password)
        # Create the user document based on the user schema.
        new_user = {
            "username": username,
            "password": hashed_password,
            "email": "",  # We can add email field later when we implement the account page.
            "liked_posts": [],
            "sent_posts": []
        }
        dbm.add_user_to_db(db, new_user)
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
    Fetch posts from MongoDB.
    """
    query = request.args.get('query', '')
    terms = query.split()
    regular_terms = []
    advanced_terms = {}

    availability_raw = request.args.get('availability', '').strip()
    listing_type = request.args.get('listing-type', '').strip()

    # Try to look for terms with advanced search syntax
    # if the key is not in the valid search list, process as regular search term
    # for example, it doesn't search for "sapiens" in the DB for "Sapiens: A Brief History of Humankind"
    for term in terms:
        if ":" in term:
            k, v = term.split(':',1)
            k, v = k.strip(), v.strip()
            if k in VALID_SEARCH_FIELDS:
                advanced_terms.setdefault(k, []).append(v)
            else:
                regular_terms.append(term.strip())
        else:
            regular_terms.append(term.strip())

    and_clauses = []
    for term in regular_terms:
        if not term:
            continue
        and_clauses.append({
            '$or': [
                {field: {"$regex": term, "$options": "i"}}
                for field in VALID_SEARCH_FIELDS
            ]
        })
    for key, values in advanced_terms.items():
        for val in values:
            and_clauses.append({key: {"$regex": val, "$options": "i"}})

    # filters
    if availability_raw in ('true', 'false'):
        and_clauses.append({"available": (availability_raw == "true")})
    if listing_type:
        and_clauses.append({"listing_type": listing_type})

    filter_query = {"$and": and_clauses} if and_clauses else {}
    books = db.posts.find(filter_query)

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

    # For GET requests
    # For the IDs stored in liked_posts
    # find all post IDs that the user liked, notice some might be deleted
    liked_ids = current_user.liked_posts
    # ids exist in both liked_posts and the posts collection
    found_books = list(db.posts.find({"_id": {"$in": liked_ids}}))
    found_ids = [post['_id'] for post in found_books]
    ghost_ids = list(set(liked_ids) - set(found_ids))
    if ghost_ids:
        db.users.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$pull": {"liked_posts": {"$in": ghost_ids}}}
        )
    # for the IDs stored in sent_posts
    sent_books = list(db.posts.find({"_id": {"$in": current_user.sent_posts}}))

    return render_template('account.html',
                           liked_books=found_books,
                           sent_books=sent_books)

@app.route('/edit_post/<post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    """
    In the account page, the lender can edit the post they sent.
    """
    post = db.posts.find_one({"_id": ObjectId(post_id), "sender_id": ObjectId(current_user.id)})
    if not post:
        flash("Post not found or unauthorized.", "error")
        return redirect(url_for('account'))

    if request.method == 'POST':
        # Capture the updated fields
        title = request.form.get('title')
        author = request.form.get('author')
        listing_type = request.form.get('listing_type')
        price = request.form.get('price')
        other_info = request.form.get('other_info')
        available = request.form.get('available') == 'on' # Checkbox logic

        updated_fields = {
            "title": title,
            "author": author,
            "listing_type": listing_type,
            "price": float(price) if price and listing_type == 'Selling' else None,
            "other_info": other_info,
            "available": available
        }
        db.posts.update_one(
            {"_id": ObjectId(post_id), "sender_id": ObjectId(current_user.id)},
            {"$set": updated_fields}
        )
        flash("Post updated successfully!", "success")
        return redirect(url_for('account'))
    return render_template('edit_post.html', post=post)


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

    post = db.posts.find_one({"_id": p_id, "sender_id": user_id})
    if not post:
        # 403 means the server does not allow this action.
        # This should never happen because the delete button should only show for the lender,
        # but good to have just in case.
        return {"error": "Can't find this post or it's sender!"}, 403
    # Delete all images of this post.
    post_images = post.get('images', [])
    for filename in post_images:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Deleted file: {file_path}") # for debugging
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")

    # Remove this post's ID from this user's 'sent_posts' field.
    db.users.update_one({"_id": user_id}, {"$pull": {"sent_posts": p_id}})
    # Remove this post's ID from the posts collection.
    db.posts.delete_one({"_id": p_id})

    # Clean up other users' liked lists.
    # db.users.update_many({"liked_posts": p_id}, {"$pull": {"liked_posts": p_id}})
    # But this would be slow if many users.
    # So we implement another way. See the docstring above for details.
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
        # Get the form data for the new post from request.
        title = request.form.get('title')
        author = request.form.get('author')
        listing_type = request.form.get('listing_type') # lending/selling/donating/showing off.
        price = request.form.get('price') # maybe empty if not selling.
        # print("Price is:", price, "Its type is", type(price)) # for debugging.
        other_info = request.form.get('other_info')
        files = request.files.getlist('images')
        # Check if verify all files have valid extensions before saving anything.
        for file in files:
            if file and file.filename:
                if not allowed_file(file.filename):
                    flash(f"We only support {', '.join(ALLOWED_EXTENSIONS)}.", "error")
                    return render_template('create_post.html')
        # Handle uploaded images
        image_filenames = []
        for file in files:
            if file and file.filename:
                file_ext = file.filename.rsplit('.', 1)[1].lower()
                # new filename: user_id + random_uuid + original_ext
                file_newname = f"{current_user.id}_{uuid_uuid4().hex}.{file_ext}"
                file_newname = secure_filename(file_newname)
                # make sure the folder to store images exists. If not, create one.
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_newname))
                image_filenames.append(file_newname)
        new_post = {
            "title": title,
            "author": author,
            "listing_type": listing_type,
            "price": float(price) if price else None,
            "images": image_filenames, # a list of images uploaded.
            "other_info": other_info,
            "sender_id": ObjectId(current_user.id), # sender as in post sender.
            "sender_name": current_user.username,
            # "sender_email": current_user.email,
            # If a user changes their email. This post might be fucked up.
            # Make the logic clearer. We can discuss later.
            'num_ppl_wanted': 0,
            "created_at": datetime.datetime.now(datetime.timezone.utc),
            "available": True
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
    # Should never happen since this button only exists for existing posts. But good to have.
    if not current_bk:
        return {"error": "Book not found"}, 404
    # Check if current user sent this post.
    if str(current_bk.get('sender_id')) == str(current_user.id):
        return {"error": "Are you trying to like your own post? LOL"}, 400
    # Check if curr_user has already liked this book.
    liked_posts = current_user.liked_posts
    if bk_id in liked_posts:
        # post already liked, so unlike this post by removing ID from current user's liked_posts
        db.users.update_one(
            {"_id": user_id},
            {"$pull": {"liked_posts": bk_id}}
        )
        like_num_change = -1
        action = "unlike"
    else:
        # liking the post, add post ID to curr_user's liked_posts
        db.users.update_one(
            {"_id": user_id},
            {"$push": {"liked_posts": bk_id}}
        )
        like_num_change = 1
        action = "like"
    # Update this book's corresponding fields
    result = db.posts.find_one_and_update(
        {"_id": bk_id},
        {"$inc": {"num_ppl_wanted": like_num_change}},
        return_document=True # Make the function return the updated doc
    )
    return {
        "new_count": result.get('num_ppl_wanted', 0),
        "action": action
    }, 200

@app.route('/book/<book_id>')
@login_required
def book_details(book_id):
    """
    Displays detailed data for this book.
    This page has two parents: home and account.
    We allow users to go back to their previous page.
    We also fetch the sender's user 
    """
    book = db.posts.find_one({"_id": ObjectId(book_id)})
    user = db.users.find_one({"_id": book.get('sender_id')}) if book else None
    back_url = request.referrer
    if not book:
        flash("Book not found!", "error")
        return redirect(url_for('home'))
    return render_template('book_details.html', book=book, user=user, back_url=back_url)

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
