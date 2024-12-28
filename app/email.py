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

from threading import Thread
from flask import current_app
from flask_mail import Message
from app import mail


# pylint: disable=redefined-outer-name
def send_async_email(app, msg):
    """
    Sends an email asynchronously.

    This function is used as the target for the thread that sends
    the email in the background. It takes the Flask application
    context and the email message to senf the email.

    Args:
        app (Flask): The Flask application instance.
        msg (Message): The email message to send.
    """
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    """
    Constructs an email messafe and sends it asynchronously.

    This function creates a Message object with the provided subject,
    sender, recipients, and body content (both plain text and HTML).
    It then starts a new thread to send the email asynchronously.

    Args:
        subject (str): The subject of the email
        sender (str): The sender's email address
        recipients (list): A list of recipient email address.
        text_body (str): The plain text body of the email.
        html_body (str): The HTML body of the email.
    """
    # Create a new email message object
    msg = Message(subject, sender=sender, recipients=recipients)

    # Set the plain-text and HTML bodies of the email
    msg.body = text_body
    msg.html = html_body

    # Send email asynchronously
    # pylint: disable=protected-access
    Thread(
        target=send_async_email, args=(current_app._get_current_object(), msg)
    ).start()
