from app import app
from app.forms import LoginForm
from flask import render_template


@app.route("/")
@app.route("/index")
def index():
    user = {"username": "Sakhile"}
    posts = [
        {
            "author": {"username": "Sakhile"},
            "body": "Plyaing with Flask, Jinja and some HTML!",
        },
        {
            "author": {"username": "Elon"},
            "body": "Final preparations for Starship Flight 6 🚀 on 18 November!",
        },
    ]
    return render_template("index.html", title="Home", user=user, posts=posts)


@app.route("/login")
def login():
    form = LoginForm()
    return render_template("login.html", title="Sign In", form=form)
