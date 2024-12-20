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
from flask_babel import _, lazy_gettext as _l
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


# pylint: disable=too-few-public-methods
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

    username = StringField(_l("Username"), validators=[DataRequired()])
    password = PasswordField(_l("Password"), validators=[DataRequired()])
    remember_me = BooleanField(_l("Remember Me"))
    submit = SubmitField(_l("Sign In"))


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

    username = StringField(_l("Username"), validators=[DataRequired()])
    email = StringField(_l("Email"), validators=[DataRequired(), Email()])
    password = PasswordField(_l("Password"), validators=[DataRequired()])
    password2 = PasswordField(
        _l("Repeat Password"), validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField(_l("Register"))

    def validate_username(self, username):
        """Ensure that the username is unique."""
        user = db.session.scalar(sa.select(User).where(User.username == username.data))
        if user is not None:
            raise ValidationError(_("Please use a different username."))

    def validate_email(self, email):
        """Ensure that the email is unique."""
        user = db.session.scalar(sa.select(User).where(User.email == email.data))
        if user is not None:
            raise ValidationError(_("Please use a different email address."))


# pylint: disable=too-few-public-methods
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

    username = StringField(_l("Username"), validators=[DataRequired()])
    about_me = TextAreaField(_l("About me"), validators=[Length(min=0, max=140)])
    submit = SubmitField(_l("Submit"))

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
                raise ValidationError(_("Please use a different username."))


# pylint: disable=too-few-public-methods
class EmptyForm(FlaskForm):
    """
    A form used for actions that do not require additional input from the user,
    such as following or unfollowing.

    Fields:
    - submit: The submit button to submit the form.
    """

    submit = SubmitField("Submit")


# pylint: disable=too-few-public-methods
class PostForm(FlaskForm):
    """
    A form for creating or editing a post.

    The form uses the following validators for the 'post' field:
    - DataRequired: Ensures the field is not empty.
    - Length: Restricts the length of the input to be between 1 and 140 characters.

    Attributes:
        post (TextAreaField): The text area for the post content.
        submit (SubmitField): The submit button for the form.
    """

    post = TextAreaField(
        _l("Say something"), validators=[DataRequired(), Length(min=1, max=140)]
    )
    submit = SubmitField(_l("Submit"))


# pylint: disable=too-few-public-methods
class ResetPasswordRequestForm(FlaskForm):
    """
    A form for requesting a password reset.

    This form is used to collect the user's email address when they want to request
    a password reset. It includes validation for a properly formatted email address.

    Attributes:
        email (StringField): The email address field, which must be a valid email
                              and cannot be empty.
        submit (SubmitField): A submit button to request the password reset.

    Methods:
        validate(): Inherits from FlaskForm; validates the form data, ensuring that
                    the email field contains a valid, non-empty email address.
    """

    email = StringField(_l("Email"), validators=[DataRequired(), Email()])
    submit = SubmitField(_l("Request Password Reset"))


# pylint: disable=too-few-public-methods
class ResetPasswordForm(FlaskForm):
    """
    A form for resetting the user's password. It includes fields for the new password
    and its confirmation, along with a submit button.

    Attributes:
        password (PasswordField): A field for entering the new password, which is required.
        password2 (PasswordField): A field for confirming the new password, which must
        match the 'password' field.
        submit (SubmitField): A submit button to submit the form.
    """

    password = PasswordField(_l("Password"), validators=[DataRequired()])
    password2 = PasswordField(
        _l("Repeat Password"), validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField(_l("Request Password Reset"))
