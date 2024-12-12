"""
Flask application setup for the Chronicles project.

This module sets up the core components of a Flask application, including:

- Flask app configuration loaded from a Config object
- SQLAlchemy for database handling
- Flask-Login for user authentication management
- Flask-Migrate for database migrations
- Logging setup for error tracking with email notifications and file logging
"""

import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from config import Config

# Initialize the Flask application and other extensions
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = "login"
mail = Mail(app)

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
