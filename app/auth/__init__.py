"""
auth module for user authentication.

This module defines a Blueprint named 'auth' that manages routes and 
views related to user authentication, including login, registration, 
and account management.
"""

from flask import Blueprint

bp = Blueprint("auth", __name__)
# pylint: disable:wrong-import-position
from app.auth import routes
