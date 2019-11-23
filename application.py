import os
import requests

from flask import Flask, session, render_template, redirect, url_for, request, flash, abort, escape, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    if session.get("username"):
        return redirect(url_for("search"))
    return render_template("index.html")


@app.route("/api/")
@app.route("/api/<string:isbn>")
def api(isbn=""):
    if isbn:
        result = db.execute("SELECT * from books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
        if result:
            json_data = dict()
            _id = result.id
            ratings_count = db.execute("SELECT COUNT(*) FROM reviews WHERE book_id = :_id", {"_id": _id}).fetchone()[0]
            ratings_average = db.execute("SELECT AVG(rating) FROM reviews WHERE book_id = :_id", {"_id": _id}).fetchone()[0]
            json_data["title"] = result.title
            json_data["author"] = result.author
            json_data["year"] = result.year
            json_data["isbn"] = result.isbn
            json_data["review_count"] = ratings_count
            try:
                json_data["average_score"] = float(ratings_average)
            except TypeError:
                json_data["average_score"] = 0
            return jsonify(json_data)
        else:
            abort(404)
    else:
        return render_template("api.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username == "" or password == "":
            flash("Username and password fields must be filled in.", "danger")
            return render_template("signup.html")
        if len(password) < 8:
            flash("Password too short. Must be at least 8 characters.", "danger")
            return render_template("signup.html")
        if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount != 0:
            flash("Username not available. Please choose another username.", "danger")
            return render_template("signup.html")
        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
                   {"username": username, "password": password})
        db.commit()
        session['username'] = username
        result = db.execute("SELECT id FROM users WHERE username = :username", {"username": username}).fetchone()
        session['userid'] = result.id
        return redirect(url_for("search"))
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username == "" or password == "":
            flash("Username and password fields must be filled in.", "danger")
            return render_template("login.html")
        user = db.execute("SELECT * FROM users WHERE username = :username AND password = :password",{"username": username, "password": password}).fetchone()
        if not user:
            flash("Username or password is wrong. Please try again.", "danger")
            return render_template("login.html")
        session['username'] = user.username
        session['userid'] = user.id
        return redirect(url_for("search"))
    return render_template("login.html")


@app.route("/logout")
def logout():
    if session.get("username"):
        session.pop('username')
    return redirect(url_for('index'))


@app.route("/search", methods=["GET", "POST"])
def search():
    if session.get("username") is None:
        flash("You need to log in first.", "danger")
        return redirect(url_for("login"))
    if request.method == "POST":
        q = request.form.get("q")
        if q:
            books = []
            query = "%" + q.upper() + "%"
            result = db.execute("SELECT * FROM books WHERE isbn LIKE :query", {"query": query}).fetchall()
            if result:
                books.extend(result)
            result = db.execute("SELECT * FROM books WHERE upper(title) LIKE :query", {"query": query}).fetchall()
            if result:
                books.extend(result)
            result = db.execute("SELECT * FROM books WHERE upper(author) LIKE :query", {"query": query}).fetchall()
            if result:
                books.extend(result)
            if len(books) == 0:
                flash(f"No results found for '{q}'.", "info")
            return render_template("search.html", q=q, books=books)
    return render_template("search.html")


@app.route("/book/<string:_id>", methods=["GET", "POST"])
def book(_id=""):
    if session.get("username") is None:
        flash("You need to log in first.", "danger")
        return redirect(url_for("login"))
    if request.method == "POST":
        rating = request.form.get("rating")
        review = request.form.get("review")
        if review is None:
            review = ""
        else:
            review = escape(review)
        user_id = session["userid"]
        has_review = db.execute("SELECT id FROM reviews WHERE user_id = :user_id AND book_id = :_id", {"user_id": user_id, "_id": _id}).fetchone()
        if has_review:
            db.execute("UPDATE reviews SET rating = :rating, review = :review, review_date = NOW() WHERE id = :id", {"rating": rating, "review": review, "id": has_review.id})
        else:
            db.execute("INSERT INTO reviews (user_id, book_id, review, rating, review_date) VALUES (:user_id, :_id, :review, :rating, NOW() )", {"user_id": user_id, "_id": _id, "review": review, "rating": rating})
        db.commit()
    book_details = db.execute("SELECT * FROM books WHERE id = :_id", {"_id": _id}).fetchone()
    if book_details is None:
        abort(404)
    res = requests.get("https://www.goodreads.com/book/review_counts.json",
                       params={"key": "Ayh56PvLyBKUhzAACQI8g", "isbns": book_details[1]})
    if res.status_code == 200:
        goodreads = res.json()['books'][0]
    else:
        goodreads = None
    reviews = db.execute("SELECT username, rating, review, review_date FROM reviews JOIN users ON users.id = reviews.user_id WHERE book_id = :_id ORDER BY review_date DESC", {"_id": _id}).fetchall()
    # ratings_count = len(reviews)
    ratings_count = db.execute("SELECT COUNT(*) FROM reviews WHERE book_id = :_id", {"_id": _id}).fetchone()[0]
    ratings_average = db.execute("SELECT AVG(rating) FROM reviews WHERE book_id = :_id", {"_id": _id}).fetchone()[0]
    return render_template("book.html", book_details=book_details, goodreads=goodreads, reviews=reviews, ratings_count=ratings_count, ratings_average=ratings_average)
