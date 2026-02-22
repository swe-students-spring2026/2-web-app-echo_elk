# Web Application Exercise

A little exercise to build a web application following an agile development process. See the [instructions](instructions.md) for more detail.

## Product vision statement

See instructions. Delete this line and place the Product Vision Statement here.

## User stories

See instructions. Delete this line and place a link to the user stories here. (Delete this before submission).

Note: According to the instruction, user stories should be created as Issues in the team's GitHub repository.
A link to the Issues page should be included in the README.md file. (Delete this before submission).

### User Type A (Book Lender/Seller):

As a book lender/seller, I want to keep track of all books that I finished reading and wanted to lend in the platform, so that I will not mix up with other books I haven't read.

As a book lender/seller, I want to send a post about a book that I want to lend, so that other people can see the books that I want to lend.

As a book lender/seller, I want to add more infomation about the book in the post, so that other people can look into the post to see if the book is what they are looking for.

As a book lender/seller, I want to delete posts, so that I know the book that the post shows has been lent and I will not mix them up with books I haven't lent.

As a book lender/seller, I want to be able to add an attribute to a post about whether I'm selling or lending this book, so that other people can know my intention clearly.

As a book lender/seller, I want to be able to set the selling/rental price of my book, so that I can control my earnings based on the value of the book.

As a book lender/seller, I want to set a book as pending or available, so that I stop receiving unneeded messages if I am already negotiating with a number of buyers/borrowers.

As a book lender, I want to see borrower ratings and reviews before approving a request so that I feel secure lending my book.

As a book lender, I want to set and keep track of the length of the rental period, so that I can get my book back on time.

### User Type B (Book Borrower/Buyer)

As a book borrower/buyer, I want to see how many people want to borrow the book in a post, so that I can estimate my chance of getting this book and act accordingly.

As a book borrower/buyer, I want to see all the posts that have books I like in a hub, so that I can have a clear view of all the books I want to borrow/buy.

As a book borrower/buyer, I want to delete/unlike posts in a hub after I do not want the book anymore or I have already got the book, so that the hub only shows books I don't have clearly.

As a book borrower/buyer, I want to have a search bar to look for books I want, so that I can find books more efficiently.

As a book borrower/buyer, I want to see the contact information of the person who sent the post, so that I can get talk with them about the book I want.

As a book borrower/buyer, I want to filter book by genre, so that I can browse specifically for books that are to my taste.

As a book borrower/buyer, I want to compare prices between listings of the same book so that I can get a better deal.


[Link to our Issues page!](https://github.com/swe-students-spring2026/2-web-app-echo_elk/issues)
## Steps necessary to run the software

See instructions. Delete this line and place instructions to download, configure, and run the software here.

```shell
# First, clone this repository.
git clone https://github.com/swe-students-spring2026/2-web-app-echo_elk.git
```

If you use a windows, switch to git bash and then proceed. If you use a unix-like os, just proceed.

```shell
# Setup a python virtual environment (venv/.venv).
python -m venv venv
```

```shell
# Activate the virtual environment.
source venv/Scripts/activate
```

```shell
# Install flask, pymongo, dotenv, in your venv.
pip install flask flask-login pymongo dotenv
```

To run the following command, download `mongosh` [here](https://www.mongodb.com/try/download/shell) (*the default command line client program*.)
```shell
# Connect to the database server database's connection string:
mongosh "mongodb+srv://2-web-app-echo-elk.8e6mdjj.mongodb.net/" --apiVersion 1 --username echo-elk
# You will be prompted to enter your database user password after running that command.
```

```shell
# define a unique name for the database.
use your_db_name # e.g. echo-elk
```

```shell
# prove that you are logged into a Javascript command-line interface to MongoDB.
1+1
# if you see 2, things work out fine!
```

```shell
# To exit mongosh, type:
exit
```

## Task boards

[Link to our Task Board!](https://github.com/orgs/swe-students-spring2026/projects/34/views/2)
