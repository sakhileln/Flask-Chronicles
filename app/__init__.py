"""
Flask application setup for the Chronicles project.

This module sets up the core components of a Flask application, including:

- Flask app configuration loaded from a Config object
- SQLAlchemy for database handling
- Flask-Login for user authentication management
- Flask-Migrate for database migrations
- Logging setup for error tracking with email notifications and file logging
"""

# pylint: disable=cyclic-import
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from flask_moment import Moment
from flask_babel import Babel, lazy_gettext as _l
from config import Config


def get_locale():
    """
    Determine the best matching locale for the application based on the
    client's accepted languages.

    This function checks the 'Accept-Language' header sent by the client
    and returns the most suitable language from the application's
    configured languages.

    Returns:
        str: The best matching locale as a string, or None if no match is found.
    """
    return request.accept_languages.best_match(app.config["LANGUAGES"])


# Initialize the Flask application and other extensions
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = "login"
login.login_message = _l("Please log in to access this page.")
mail = Mail(app)
moment = Moment(app)
babel = Babel(app, locale_selector=get_locale)

# Logging configuration to handle errors and send notifications
if not app.debug:
    if app.config["MAIL_SERVER"]:
        # pylint: disable=invalid-name
        auth = None
        if app.config["MAIL_USERNAME"] or app.config["MAIL_PASSWORD"]:
            auth = (app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])
        # pylint: disable=invalid-name
        secure = None
        if app.config["MAIL_USE_TLS"]:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config["MAIL_SERVER"], app.config["MAIL_PORT"]),
            fromaddr="no-reply@" + app.config["MAIL_SERVER"],
            toaddrs=app.config["ADMINS"],
            subject="⛔ Flask Chronicles Failure❗",
            credentials=auth,
            secure=secure,
        )
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

    # File handler for logging application events to a file
    if not os.path.exists("logs"):
        os.mkdir("logs")
    file_handler = RotatingFileHandler(
        "logs/flask_chronicles.log", maxBytes=10240, backupCount=10
    )
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
        )
    )
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info("Flask Chronicles startup")

# Import application routes, models, and error handlers
# pylint: disable=wrong-import-position
from app import routes, models, errors
