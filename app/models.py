from app import db, login
from datetime import datetime, timezone
from flask_login import UserMixin
from hashlib import md5
import sqlalchemy as sa
import sqlalchemy.orm as so
from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    """
    A class repersenting a user in the database

    Attributes:
        id (int): Primary key identifier for the user.
        username (str): Username choosen by the user (unique).
        email (str): User's email address (unique and indexed).
        password_hash (Optional[str]): Hanshed password for user.
            May be None if not set
        posts (str): A relationship back to the Post model, representing the post
    Nethids:
        __repr__: Returns a string representation of User instance.
    """

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    posts: so.WriteOnlyMapped["Post"] = so.relationship(back_populates="author")

    def __repr__(self) -> str:
        """
        Returns a string representation of the User object.

        Returns:
            str: A string in the format "<User username>" for debugging.
        """
        return "<User {}>".format(self.username)

    def set_password(self, password: str) -> None:
        """
        Sets the password for the user by hashing the provided plain-text password.

        Args:
            password (str): The plain-text password that needs to be hashed and stored.
        Returns:
            None
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """
        Checks if the provided plain-text password matches the stored hashes password.

        Args:
            passowrd (str): The plain-text password to check against the stored hash.
        Returns:
            bool: True if password matches the stored password, False otherwise
        """
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        return f"https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'"


class Post(db.Model):
    """
    A class representing a post in the database.

    Attributes:
        id (int): The primary key identifier for the post.
        body (str): Content of the post (limited ti 140 chracters).
        timestamp (datetime): The time when post was created, in UTC+2.
        user_id (int): Foreign key referencing the User who created the post.
        author (User): A relationship back to the User model, representing the author

    Methods:
        __repr__: Returns a string representing of the Post instance.
    """

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc)
    )
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    author: so.Mapped[User] = so.relationship(back_populates="posts")

    def __repr__(self) -> str:
        """
        Returns a string representation of the Post object.

        Returns:
            str: Astring in the format "<Post body>" for debugging.
        """
        return f"<Post {self.body}>"


# Flask-Login user loader function
@login.user_loader
def load_user(id):
    """
    Loads a user from the database by their ID.

    Args:
        id (int): The ID of the user to load.
    Returns:
        User: The user object corresponding to the given ID, or None if not found.
    """
    return db.session.get(User, int(id))
