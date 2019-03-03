import os
import requests

from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
import db

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

book_key = os.getenv("GOODREADS_KEY")


@app.route("/")
def index():
    """
    login page
    """
    if 'username' not in session:
        return render_template("login.html")
    else:
        return redirect(url_for('books'))


@app.route("/signup")
def signup():
    """
    signup page
    """
    return render_template("signup.html")


@app.route("/login", methods=["POST"])
def login():
    """
    login procedure
    """
    if request.method != "POST":
        return render_template("error.html", "Can not accessible")
    username = request.form.get("username")
    password = request.form.get("password")

    # check user information
    if username is None or password is None:
        return render_template("error.html", message="empty login info")

    # check login info
    if db.is_registered_user(username, password):
        session['username'] = username
        return redirect(url_for('books', username=session['username']))
    else:
        return render_template("error.html", message="No such a user", login_url=True)


@app.route("/logout")
def logout():
    """
    logout procedure
    """
    try:
        session.pop('username')
    except KeyError:
        print('')
    finally:
        return redirect(url_for("index"))


@app.route("/newuser", methods=["POST"])
def newuser():
    """
    Add a new user to db and redirect main search page
    """
    if request.method != "POST":
        return render_template("error.html", message="Can not accessible")

    username = request.form.get("username")
    password = request.form.get("password")
    if db.is_user(username):
        return render_template("error.html", message="Username already exists.")

    if len(password) == 0:
        return render_template("error.html", message="check your password")

    db.create_user(username, password)
    session['username'] = username
    return redirect(url_for('books'))


@app.route("/books")
def books():
    """

    """
    if 'username' not in session:
        return redirect(url_for("index"))
    return render_template("main.html", username=session['username'])


@app.route("/search", methods=["POST"])
def book_search():
    if 'username' not in session:
        return redirect(url_for("index"))

    keyword = request.form.get("keyword")
    books = db.find_books(keyword.replace("'", ""))

    return render_template("search_results.html", username=session['username'], book_keyword=keyword, books=books)


@app.route("/book/<isbn>")
def book(isbn):
    if 'username' not in session:
        return redirect(url_for('index'))

    aBook = db.book_info(isbn)
    if aBook is None:
        return render_template("error.html", message="No such a book")

    reviews = db.book_reviews(aBook.book_id)
    rating = bookinfo_goodreads(isbn)
    return render_template("book.html", username=session['username'], aBook=aBook, reviews=reviews, rating=rating)


@app.route("/add_review/<isbn>/<username>", methods=["POST"])
def add_review(isbn, username):
    review = request.form.get("user_review")

    if review is None or len(review) == 0:
        return redirect(url_for('book',isbn=isbn))

    db.add_review(isbn, username, review)
    return redirect(url_for('book', isbn=isbn))


@app.route("/delete_review/<isbn>/<username>", methods=["GET", "POST"])
def delete_review(isbn, username):
    if request.method == "POST":
        db.delete_review(isbn, username)
    return redirect(url_for('book', isbn=isbn))


def bookinfo_goodreads(isbn):
    """
    get book information from goodreads.com
    """
    res = requests.get("https://www.goodreads.com/book/review_counts.json",
                       params={"key": book_key, "isbns": isbn})
    res = res.json()
    if res:
        rating_info = dict()
        rating_info['count'] = res['books'][0]['work_ratings_count']
        rating_info['avg_rating'] = res['books'][0]['average_rating']
        return rating_info
    else:
        return None
