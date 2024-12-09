"""
This module defines the forms used in the Flask application, utilizing Flask-WTF for form handling
and WTForms for validation. These forms are used for user login, registration, profile editing,
and other interactions within the application.

Classes:
- LoginForm: Form used for user login.
- RegistrationForm: Form used for new user registration.
- EditProfileForm: Form used for editing user profile.
- EmptyForm: A form used for following and unfollowing actions.
"""

from flask_wtf import FlaskForm
import sqlalchemy as sa
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import (
    ValidationError,
    DataRequired,
    Email,
    EqualTo,
    Length,
)
from app import db
from app.models import User


class LoginForm(FlaskForm):
    """
    Form used for user login, including fields for username, password,
    and a 'Remember Me' checkbox.

    Fields:
    - username: The user's username, which is required.
    - password: The user's password, which is required.
    - remember_me: A boolean checkbox indicating whether to remember the user.
    - submit: The submit button to submit the form.
    """

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class RegistrationForm(FlaskForm):
    """
    Form used for user registration, with fields for username, email, password,
    and password confirmation.

    Fields:
    - username: The user's username, which is required.
    - email: The user's email, which is required and validated to be in a proper format.
    - password: The user's password, which is required.
    - password2: A confirmation field to ensure password match.
    - submit: The submit button to submit the form.

    Methods:
    - validate_username: Ensures that the username is unique.
    - validate_email: Ensures that the email is unique.
    """

    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")

    def validate_username(self, username):
        """Ensure that the username is unique."""
        user = db.session.scalar(sa.select(User).where(User.username == username.data))
        if user is not None:
            raise ValidationError("Please use a different username.")

    def validate_email(self, email):
        """Ensure that the email is unique."""
        user = db.session.scalar(sa.select(User).where(User.email == email.data))
        if user is not None:
            raise ValidationError("Please use a different email address.")


class EditProfileForm(FlaskForm):
    """
    Form used for editing a user's profile, with fields for changing the username
    and providing a short bio or "About Me" description.

    Fields:
    - username: The user's username, which is required.
    - about_me: A text area where the user can write a short bio (max 140 characters).
    - submit: The submit button to submit the form.

    Methods:
    - validate_username: Ensures the new username is unique, if it has changed.
    """

    username = StringField("Username", validators=[DataRequired()])
    about_me = TextAreaField("About me", validators=[Length(min=0, max=140)])
    submit = SubmitField("Submit")

    def __init__(self, original_username, *args, **kwargs):
        """Initialize the form with the original username for comparison."""
        super().__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        """Ensure that the username is unique (if changed)."""
        if username.data != self.original_username:
            user = db.session.scalar(
                sa.select(User).where(User.username == username.data)
            )
            if user is not None:
                raise ValidationError("Please use different username.")


class EmptyForm(FlaskForm):
    """
    A form used for actions that do not require additional input from the user,
    such as following or unfollowing.

    Fields:
    - submit: The submit button to submit the form.
    """

    submit = SubmitField("Submit")
