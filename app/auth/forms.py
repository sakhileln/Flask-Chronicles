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

import sqlalchemy as sa
from flask_wtf import FlaskForm
from flask_babel import _, lazy_gettext as _l
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
)
from wtforms.validators import (
    ValidationError,
    DataRequired,
    Email,
    EqualTo,
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
        user = db.session.scalar(sa.select(User).where(User.username == username.data))
        if user is not None:
            raise ValidationError(_("Please use a different username."))

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(User.email == email.data))
        if user is not None:
            raise ValidationError(_("Please use a different email address."))


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
