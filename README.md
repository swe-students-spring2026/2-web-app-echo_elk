## Book Exchange
 Book Exchange is an online marketplace designed for students to exchange second-hand books. You can create an account to send posts about books for sale, loan, or donation, while browsing a diverse community library of available books from other users.

## Steps necessary to run the software
> If we are deploying this app, do we still need to show these steps?

```shell
# First, clone this repository.
git clone https://github.com/NarezIn/Book-Exchange.git
```

If you use a windows, switch to git bash and then proceed. If you use a unix-like os, just proceed.

Second, create a virtual environmenet using `pipenv`.

Please make sure you global python interpreter has `pipenv` installed.

If not, do this:
```shell
# Make sure you install 'pipenv' in your prefered 'python.exe'.
# To see if your prefered python interpreter is the top choice:
where python
```
```shell
# install pipenv globally
pip install pipenv
```
After you have `pipenv` installed,
```shell
# Activate a virtual environment and drop yourself into a new shell that uses that virtualenv’s python.
pipenv shell
``` 
```shell
# Install the modules
pipenv install Flask flask-login pymongo python-dotenv cloudinary
```

<!-- 
The out-dated/old-fashioned way to set up a python virtual environment (`venv` in this case).

```shell
# Setup a python virtual environment using pipvenv.
python -m venv venv
```

```shell
# Activate the virtual environment.
source venv/Scripts/activate
```

```shell
# Install flask, pymongo, dotenv, flask-login in your venv.
pip install flask flask-login pymongo dotenv cloudinary
```
-->

- Make sure you did your thing in the editor to select the virtual environment to be the interpreter of the app.py file.
    - You would see the path to the designated virtual  environment in your shell after you ran `pipenv shell`, which is what you did before.
    - Select that path as the interpreter.

- You need one of our team members to have your IP-address so you can access our mongodb atlas database.
- You also need to create an `.env` file to define `MONGO_DBNAME`, 
`MONGO_URI`, and
`SECRET_KEY`, which are some global variables that our app depends on.

Last step:
```shell
# Run the app!
python app.py
```
Now you should see a link in your shell. Click it and play around.


#### If you want to directly play around the database on your shell...
Run the following command. Make sure you have downloaded `mongosh` [here](https://www.mongodb.com/try/download/shell) (*the default command line client program*.)
```shell
# Connect to the database server:
mongosh "mongodb+srv://2-web-app-echo-elk.8e6mdjj.mongodb.net/" --apiVersion 1 --username echo-elk
# You will be prompted to enter your database user password. Enter your password.
```

```shell
# After you access our databse, prove that you are logged into a Javascript command-line interface to MongoDB.
1+1
# You would expect to see 2!
```

```shell
# Go into the database that we store users and posts information。
use echo-elk
```

If you want to create a new database.
```shell
# define a unique name for the database.
use your_db_name
```

We have two collections in `echo-elk`, they are `users` and `posts`.

```shell
# Have a look of all documents in users
db.users.find()
# Have a look of all documents in posts
db.posts.find()
```

```shell
# To exit mongosh:
exit
```

## Task boards

[Link to our Task Board!](https://github.com/users/NarezIn/projects/2/views/3)
