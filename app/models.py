from app import db
import sqlalchemy as sa
import sqlalchemy.orm as so
from typing import Optional


class User(db.Model):
    """
    A class repersenting a user in the database

    Attributes:
        id (int): Primary key identifier for the user.
        username (str): Username choosen by the user (unique).
        email (str): User's email address (unique and indexed).
        password_hash (Optional[str]): Hanshed password for user.
            May be None if not set
    Nethids:
        __repr__: Returns a string representation of User instance.
    """

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), unique=True)
    email: so.Mapped[str] = so.mapped_column(
        sa.String(120), index=True, unique=True
    )
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    def __repr__(self) -> str:
        """
        Returns a string representation of the User object.

        Returns:
            str: A string in the format "<User username>" for debugging.
        """
        return "<User {}>".format(self.username)
