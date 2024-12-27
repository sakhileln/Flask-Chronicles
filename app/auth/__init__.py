"""
auth module for user authentication.

This module defines a Blueprint named 'auth' that manages routes and 
views related to user authentication, including login, registration, 
and account management.
"""

from flask import Blueprint

bp = Blueprint("auth", __name__)

from app.auth import routes
