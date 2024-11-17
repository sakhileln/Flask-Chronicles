from app import db
from datetime import datetime, timedelta, timezone
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
        posts (str): A relationship back to the Post model, representing the post
    Nethids:
        __repr__: Returns a string representation of User instance.
    """

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), unique=True)
    email: so.Mapped[str] = so.mapped_column(
        sa.String(120), index=True, unique=True
    )
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    posts: so.WriteOnlyMapped["Post"] = so.relationship(
        back_populates="author"
    )

    def __repr__(self) -> str:
        """
        Returns a string representation of the User object.

        Returns:
            str: A string in the format "<User username>" for debugging.
        """
        return "<User {}>".format(self.username)


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
        index=True, default=lambda: datetime.now(timezone(timedelta(hours=2)))
    )
    user_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey(User.id), index=True
    )
    author: so.Mapped[User] = so.relationship(back_populates="posts")

    def __repr__(self) -> str:
        """
        Returns a string representation of the Post object.

        Returns:
            str: Astring in the format "<Post body>" for debugging.
        """
        return f"<Post {self.body}>"
