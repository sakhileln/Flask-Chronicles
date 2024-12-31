"""
Configuration class for setting up application-level settings,
including secret keys, database URI, and email settings.

This class loads configuration values from environment variables, falling
back to default values if the environment variables are not set.

Values are loaded from environment variables where possible, otherwise
falling back to default values specified in the class.
"""

import os
from dotenv import load_dotenv

# Get the absolute path to the directory where the current script is located
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


# pylint: disable=too-few-public-methods
class Config:
    """
    Configuration class for setting up application-level settings,
    including secret keys, database URI, and email settings.

    This class loads configuration values from environment variables, falling
    back to default values if the environment variables are not set.
    """

    # Secret key used for session management and cryptographic operations
    SECRET_KEY = os.environ.get("SECRET_KEY") or "a-very-secretive-thing"
    # URI for the SQLAlchemy database connection (defaults to a local SQLite database)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "blog.db")
    # Email server configuration for sending emails (e.g., for user registration)
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    # Port number for the email server (defaults to 25 if not provided)
    MAIL_PORT = int(os.environ.get("MAIL_PORT") or 25)
    # Boolean indicating whether to use TLS for the email connection
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS") is not None
    # Username for the email account (for authentication with the email server)
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    # Password for the email account (for authentication with the email server)
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    # List of administrator email addresses, typically used for sending error alerts
    ADMINS = ["sakhilelindah@gmail.com"]
    POSTS_PER_PAGE = 3
    LANGUAGES = ["en", "es"]
    MS_TRANSLATOR_KEY = os.environ.get("MS_TRANSLATOR_KEY")
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')
