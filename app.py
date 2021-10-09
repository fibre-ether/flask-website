from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from markupsafe import escape
import pandas as pd
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "password"
app.permanent_session_lifetime = timedelta(minutes = 5)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///user.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
strlist_key = "?/;"

db = SQLAlchemy(app)
db.create_all()
class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    post = db.Column(db.String(100))

    def __init__(self, name, email = None, post = None):
        self.name = name
        self.email = email
        self.post = post

class posts(db.Model):
    _id = db.Column("id", db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    title = db.Column(db.String(100))
    body = db.Column(db.String(100))

    def __init__(self, name, title = None, body = None):
        self.name = name
        self.title = title
        self.body = body




@app.route('/')
def index():
    return render_template("list.html", list=posts.query.all(), session=session)


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        if request.form["name"] == "":
            flash(" Please enter a name ", "info")
            return render_template("login.html",session=session)
        session.permanent = True
        username = request.form["name"]
        session["username"] = username

        iffound = users.query.filter_by(name=username).first()
        if iffound:
            session["email"] = iffound.email
        else:
            user = users(username)
            db.session.add(user)
            db.session.commit()
        return redirect(url_for("profile"))
    else:
        if "username" in session:
            return redirect(url_for("profile"))
        else:
            return render_template("login.html", session=session)

@app.route('/profile', methods=["POST", "GET"])
def profile():
    email = None
    if "username" in session:
        username = session["username"]
        if request.method == "POST":
            if request.form["post-title"] == "" or request.form["post-body"] == "":
                flash(" Please enter both title and post ", "info")
                return render_template("profile.html", name=username, session=session)
            post_title = request.form["post-title"]
            post_body = request.form["post-body"]
            post = posts(username, post_title, post_body)
            db.session.add(post)
            db.session.commit()
            flash(" Your post has been sent to the home page ", "info")
        elif "email" in session:
            email = session["email"]
        return render_template("profile.html", name=username, session=session)
    else:
        flash(" Please login first ", "info")
        return redirect(url_for("login"))

@app.route('/logout')
def logout():
    if "username" in session:
        user = session["username"]
        flash(f" {user} has been logged out succesfully ", "info")
    else:
        flash(" Please login first ", "info")
    session.pop("username", None)
    session.pop("email", None)
    return redirect(url_for("index"))

@app.route('/admin')
def admin():
    return redirect(url_for("index"))


if __name__ == "__main__":
    db.create_all()
    app.run(debug = True)