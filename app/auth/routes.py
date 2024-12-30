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
from urllib.parse import urlsplit

# Third-party imports
import sqlalchemy as sa
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user
from flask_babel import _

# Local application imports
# pylint: disable=cyclic-import
from app import db

# pylint: disable=cyclic-import
from app.models import User

# pylint: disable=cyclic-import
from app.auth.forms import (
    LoginForm,
    RegistrationForm,
    ResetPasswordRequestForm,
    ResetPasswordForm,
)

# pylint: disable=cyclic-import
# pylint: disable=no-name-in-module
from app.auth.email import send_password_reset_email

from app.auth import bp


@bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Route to log in a user. If the user is already authenticated,
    they are redirected to the home page.
    """
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data)
        )
        if user is None or not user.check_password(form.password.data):
            flash(_("Invalid username or password"))
            return redirect(url_for("auth.login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or urlsplit(next_page).netloc != "":
            next_page = url_for("main.index")
        return redirect(next_page)
    return render_template("auth/login.html", title=_("Sign In"), form=form)


@bp.route("/logout")
def logout():
    """
    Route to log out the current user and redirect to the home page.
    """
    logout_user()
    return redirect(url_for("main.index"))


@bp.route("/register", methods=["GET", "POST"])
def register():
    """
    Route to register a new user. If the user is already authenticated,
    they are redirected to the home page.
    """
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_("Congratulations, you are now a registered user!"))
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", title=_("Register"), form=form)


@bp.route("/reset_password_request", methods=["GET", "POST"])
def reset_password_request():
    """
    This route is used to display the form for requesting a password reset. If the user
    is already authenticated, they are redirected to the index page. If the form is submitted
    with a valid email address, the system checks if a user exists with that email, and if found,
    it sends a password reset email.

    Returns:
        - Redirect to the 'login' page if the form is successfully submitted.
        - Renders the 'reset_password_request.html' template on GET or if the form is invalid.
    """
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.email == form.email.data))
        if user:
            send_password_reset_email(user)
        flash(_("Check your email for the instructions to reset your password"))
        return redirect(url_for("auth.login"))
    return render_template(
        "auth/reset_password_request.html", title=_("Reset Password"), form=form
    )


@bp.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """
    This route handles the password reset process. It validates the token from the
    password reset link and allows the user to reset their password.

    If the user is already authenticated, they are redirected to the index page.
    If the token is invalid or expired, the user is redirected to the index page.
    If the token is valid, the user is presented with a form to reset their password.
    Upon successful form submission, the password is updated, and the user is
    redirected to the login page.

    Args:
        token (str): A token used to verify the password reset request.

    Returns:
        A redirect to either the index or login page, or a rendered password reset form.
    """
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    # pylint: disable=redefined-outer-name
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for("main.index"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_("Your password has been reset."))
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_password.html", form=form)
