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

from flask import render_template
from flask_mail import Message
from app import app, mail


def send_email(subject, sender, recipients, text_body, html_body):
    """
    Send an email using Flask-Mail.

    This function sends an email with both plain text and HTML versions of the body.
    The email is sent through the Flask-Mail extension configured in the `app` module.

    Parameters:
        subject (str): The subject of the email.
        sender (str): The email address of the sender.
        recipients (list): A list of recipient email addresses.
        text_body (str): The plain-text version of the email body.
        html_body (str): The HTML version of the email body.

    Returns:
        None: This function does not return any value. The email is sent asynchronously.
    """
    # Create a new email message object
    msg = Message(subject, sender=sender, recipients=recipients)

    # Set the plain-text and HTML bodies of the email
    msg.body = text_body
    msg.html = html_body

    # Send the email using the Flask-Mail extension
    mail.send(msg)


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
        "[Flask Chronicles] Reset Your Password",
        sender=app.config["ADMINS"][0],
        recipients=[user.email],
        text_body=render_template("email/reset_password.txt", user=user, token=token),
        html_body=render_template("email/reset_password.html", user=user, token=token),
    )
