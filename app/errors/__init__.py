"""
errors module for handling application errors.

This module defines a Blueprint named 'errors' that is used to manage 
error handling routes and their associated views in the Flask application.
"""

from flask import Blueprint

bp = Blueprint("errors", __name__)

from app.errors import handlers
