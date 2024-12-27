"""
main module for user handling.

This module defines a Blueprint named 'main' that manages routes and 
views related to user authentication, including login, registration, 
and account management.
"""

from flask import Blueprint

bp = Blueprint("main", __name__)

from app.main import routes
