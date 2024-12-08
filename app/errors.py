"""
This module contains error handling routes for the Flask application.
It defines custom error pages for HTTP 404 (Not Found) and HTTP 500 (Internal Server Error).
"""

from flask import render_template
from app import app, db


# pylint: disable=unused-argument
@app.errorhandler(404)
def not_found_error(error):
    """
    Handles 404 (Not Found) errors in the application.

    This function is triggered when a user accesses a URL that doesn't exist in the application.
    It renders a custom '404.html' template to display a friendly error message.

    Args:
        error (Exception): The error that triggered this handler.

    Returns:
        Response: The rendered '404.html' template along with the HTTP 404 status code.
    """
    return render_template("404.html"), 404


# pylint: disable=unused-argument
@app.errorhandler(500)
def internal_error(error):
    """
    Handles 500 (Internal Server Error) errors in the application.

    This function is triggered when an unexpected error occurs within the server. It ensures that
    the database session is rolled back to avoid leaving the session in an inconsistent state,
    and renders a custom '500.html' template to notify the user about the error.

    Args:
        error (Exception): The error that triggered this handler.

    Returns:
        Response: The rendered '500.html' template along with the HTTP 500 status code.
    """
    db.session.rollback()
    return render_template("500.html"), 500
