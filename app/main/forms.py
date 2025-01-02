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

from flask import request
import sqlalchemy as sa
from flask_wtf import FlaskForm
from flask_babel import _, lazy_gettext as _l
from wtforms import (
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import (
    ValidationError,
    DataRequired,
    Length,
)
from app import db
from app.models import User


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


class SearchForm(FlaskForm):
    """
    A form for searching with a single input field.

    This form is designed to handle search queries. It includes
    a required string field for the search term and disables CSRF
    protection for simplicity in GET requests.
    """

    q = StringField(_l("Search"), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        """
        Initializes the SearchForm instance.

        If no formdata is provided, it defaults to using the query
        parameters from the request. CSRF protection is disabled
        by default.
        """
        if "formdata" not in kwargs:
            kwargs["formdata"] = request.args
        if "meta" not in kwargs:
            kwargs["meta"] = {"csrf": False}
        super(SearchForm, self).__init__(*args, **kwargs)
