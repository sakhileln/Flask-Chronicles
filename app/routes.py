from app import app, db
from app.models import User
from app.forms import LoginForm
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from urllib.parse import urlsplit


@app.route("/")
@app.route("/index")
@login_required
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
    return render_template("index.html", title="Home Page", posts=posts)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data)
        )
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or urlsplit(next_page).netloc != "":
            next_page = url_for("index")
        return redirect(next_page)
    return render_template("login.html", title="Sign In", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))
