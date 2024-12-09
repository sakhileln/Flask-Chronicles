"""
This module contains routes for the Flask application, providing the core
functionality for user authentication, profile management, and interaction
with other users (such as following and unfollowing). It includes the
following routes:

- `/index` (Home Page): Displays recent posts and allows authenticated users
  to view content.
- `/login`: Allows users to log in.
- `/logout`: Logs out the current user and redirects to the home page.
- `/register`: Registers a new user.
- `/user/<username>`: Displays the profile of the specified user along with
  their posts.
- `/edit_profile`: Allows authenticated users to edit their profile.
- `/follow/<username>`: Allows users to follow another user.
- `/unfollow/<username>`: Allows users to unfollow another user.

The module also includes a `before_request` function to update the last seen
timestamp for authenticated users.

Each route uses Flask's `render_template` to render the corresponding HTML
templates, and `flash` to display messages for user actions.
"""

# Standard library imports
from datetime import datetime, timezone
from urllib.parse import urlsplit

# Third-party imports
import sqlalchemy as sa
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required

# Local application imports
# pylint: disable=cyclic-import
from app import app, db

# pylint: disable=cyclic-import
from app.models import User, Post

# pylint: disable=cyclic-import
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm, PostForm


@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
@login_required
def index():
    """
    Route for the home page, showing recent posts.
    Only accessible by authenticated users.
    """
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Your post is now live!")
        return redirect(url_for("index"))
    
    page = request.args.get("page", 1, type=int)
    posts = db.paginate(
        current_user.following_posts(),
        page=page,
        per_page=app.config["POSTS_PER_PAGE"],
        error_out=False,
    )
    next_url = (
        url_for("index", page=posts.next_num) if posts.has_next else None
    )
    prev_url = (
        url_for("index", page=posts.prev_num) if posts.has_prev else None
    )
    return render_template(
        "index.html",
        title="Home",
        form=form,
        posts=posts.items,
        next_url=next_url,
        prev_url=prev_url,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Route to log in a user. If the user is already authenticated,
    they are redirected to the home page.
    """
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        # pylint: disable=redefined-outer-name
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
    """
    Route to log out the current user and redirect to the home page.
    """
    logout_user()
    return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Route to register a new user. If the user is already authenticated,
    they are redirected to the home page.
    """
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        # pylint: disable=redefined-outer-name
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congratulations, you are now a registered user!")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


@app.route("/user/<username>")
@login_required
def user(username):
    """
    Route to view a user's profile. Shows the user's posts.
    Only accessible by authenticated users.
    """
    # pylint: disable=redefined-outer-name
    user = db.first_or_404(sa.select(User).where(User.username == username))
    page = request.args.get("page", 1, type=int)
    query = user.posts.select().order_by(Post.timestamp.desc())
    posts = db.paginate(
        query,
        page=page,
        per_page=app.config["POSTS_PER_PAGE"],
        error_out=False,
    )
    next_url = (
        url_for("user", username=user.username, page=posts.next_num)
        if posts.has_next
        else None
    )
    prev_url = (
        url_for("user", username=user.username, page=posts.prev_num)
        if posts.has_prev
        else None
    )
    form = EmptyForm()
    return render_template(
        "user.html",
        user=user,
        posts=posts.items,
        next_url=next_url,
        prev_url=prev_url,
        form=form,
    )


@app.before_request
def before_request():
    """
    A function that runs before every request. Updates the current user's
    'last_seen' timestamp if the user is authenticated.
    """
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    """
    Route for editing the current user's profile information.
    Only accessible by authenticated users.
    """
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash("Your changes have been saved.")
        return redirect(url_for("edit_profile"))
    if request.method == "GET":
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template("edit_profile.html", title="Edit Profile", form=form)


@app.route("/follow/<username>", methods=["POST"])
@login_required
def follow(username):
    """
    Route for following another user. Only accessible by authenticated users.
    """
    form = EmptyForm()
    if form.validate_on_submit():
        # pylint: disable=redefined-outer-name
        user = db.session.scalar(sa.select(User).where(User.username == username))
        if user is None:
            flash(f"User {username} not found.")
            return redirect(url_for("index"))
        if user == current_user:
            flash("You cannot follow yourself!")
            return redirect(url_for("user", username=username))
        current_user.follow(user)
        db.session.commit()
        flash(f"You are following {username}!")
        return redirect(url_for("user", username=username))

    return redirect(url_for("index"))


@app.route("/unfollow/<username>", methods=["POST"])
@login_required
def unfollow(username):
    """
    Route for unfollowing another user. Only accessible by authenticated users.
    """
    form = EmptyForm()
    if form.validate_on_submit():
        # pylint: disable=redefined-outer-name
        user = db.session.scalar(sa.select(User).where(User.username == username))
        if user is None:
            flash(f"User {username} not found.")
            return redirect(url_for("index"))
        if user == current_user:
            flash("You cannot unfollow yourself!")
            return redirect(url_for("user", username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(f"You are not following {username}.")
        return redirect(url_for("user", username=username))

    return redirect(url_for("index"))


@app.route("/explore")
@login_required
def explore():
    """
    Route for exploring all posts in descending order of their timestamp.
    Pagination:
    - The page number is obtained from the query parameter (`page`), defaulting to page 1.
    - The number of posts per page is controlled by the configuration setting `POSTS_PER_PAGE`.
    - The `next_url` and `prev_url` are generated to navigate between pages, based on the current page.

    Returns:
        A rendered template (`index.html`) displaying the posts for the current page, along with
        navigation links for previous and next pages if applicable.
    """
    page = request.args.get("page", 1, type=int)
    query = sa.select(Post).order_by(Post.timestamp.desc())
    posts = db.paginate(
        query,
        page=page,
        per_page=app.config["POSTS_PER_PAGE"],
        error_out=False,
    )
    next_url = (
        url_for("explore", page=posts.next_num) if posts.has_next else None
    )
    prev_url = (
        url_for("explore", page=posts.prev_num) if posts.has_prev else None
    )
    return render_template(
        "index.html",
        title="Explore",
        posts=posts.items,
        next_url=next_url,
        prev_url=prev_url,
    )

