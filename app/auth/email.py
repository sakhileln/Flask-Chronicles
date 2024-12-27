"""
Email utility module for sending emails using Flask-Mail.

This module provides a utility function to send emails with both plain-text and HTML
versions of the email body using the Flask-Mail extension. The function leverages the
configured `mail` object from the Flask application instance to send the emails.

Functions:
    - send_email(subject, sender, recipients, text_body, html_body):
        Sends an email with the specified subject, sender, recipients, and email bodies
        (both plain-text and HTML formats).

Dependencies:
    - Flask-Mail: The Flask extension used to handle email sending.
    - app.mail: The Flask-Mail instance initialized in the Flask application.
"""

from flask import render_template, current_app
from flask_babel import _
from app.email import send_email
    

def send_password_reset_email(user):
    """
    Sends a password reset email to the user with a reset token.

    Args:
        user (User): The user who requested a password reset. The user's
        email will be used to send the reset instructions.

    Sends an email containing a link to reset the user's password. The
    email includes both plain text and HTML versions.
    """
    token = user.get_reset_password_token()
    send_email(
        _('[Flask Chronicles] Reset Your Password'),
        sender=current_app.config['ADMINS'][0],
        recipients=[user.email],
        text_body=render_template('email/reset_password.txt', user=user, token=token),
        html_body=render_template('email/reset_password.html', user=user, token=token)
    )

