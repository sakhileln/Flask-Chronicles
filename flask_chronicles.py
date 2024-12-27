"""
This module sets up the shell context for Flask's interactive shell.

By defining the `make_shell_context` function, we add useful objects
such as the SQLAlchemy session (`db`), the SQLAlchemy ORM (`sa`), and
commonly used model classes (`User`, `Post`) to the Flask shell. This
enables a more efficient development and debugging experience by
allowing easy access to these objects from the Flask shell.

This module is typically imported during application startup in order
to configure the shell context for interactive use.

Imports:
- app: The Flask application instance.
- db: The SQLAlchemy database instance.
- User: The User model class.
- Post: The Post model class.
- sa: SQLAlchemy core module.
- so: SQLAlchemy ORM module.
"""

import sqlalchemy as sa
import sqlalchemy.orm as so
from app import create_app, db
from app.models import User, Post

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """
    Adds commonly used components to the Flask shell context.

    This function is registered with the Flask application and makes the
    following objects accessible within the interactive shell:
    - `sa`: SQLAlchemy core module.
    - `so`: SQLAlchemy ORM module.
    - `db`: The SQLAlchemy database session.
    - `User`: The User model class.
    - `Post`: The Post model class.

    Usage:
        - Access the `User` and `Post` models for querying.
        - Use `db` to interact with the database (e.g., for migrations or sessions).
        - Utilize `sa` and `so` for low-level and ORM-based SQLAlchemy operations.

    Returns:
        dict: A dictionary containing the objects to be made available in the shell.
    """
    return {'sa': sa, 'so': so, 'db': db, 'User': User, 'Post': Post}
