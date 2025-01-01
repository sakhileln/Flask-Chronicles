"""
This module defines the models for users and posts in the application. It uses SQLAlchemy
for ORM and Flask-Login for user authentication. The models define the structure of the database
and the relationships between users and posts, as well as user interactions like following
and unfollowing other users.

Classes:
- User: Represents a user in the database with fields for username, email, password, etc.
- Post: Represents a post in the database created by a user.
- followers: Association table to handle the many-to-many relationship between
            users (followers/following).
"""

from datetime import datetime, timezone
from hashlib import md5
from typing import Optional
from time import time
from flask_login import UserMixin
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app import db, login
from app.search import add_to_index, remove_from_index, query_index


# Association table for followers (many-to-many relationship)
followers = sa.Table(
    "followers",
    db.metadata,
    sa.Column("follower_id", sa.Integer, sa.ForeignKey("user.id"), primary_key=True),
    sa.Column("followed_id", sa.Integer, sa.ForeignKey("user.id"), primary_key=True),
)


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
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    following: so.WriteOnlyMapped["User"] = so.relationship(
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        back_populates="followers",
    )
    followers: so.WriteOnlyMapped["User"] = so.relationship(
        secondary=followers,
        primaryjoin=(followers.c.followed_id == id),
        secondaryjoin=(followers.c.follower_id == id),
        back_populates="following",
    )

    def __repr__(self) -> str:
        """
        Returns a string representation of the User object.

        Returns:
            str: A string in the format "<User username>" for debugging.
        """
        return f"<User {self.username}>"

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
        """
        Generates a Gravatar URL for the user based on their email.

        Args:
            size (int): The size of the avatar image to generate.
        Returns:
            str: The Gravatar URL.
        """
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        return f"https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'"

    def follow(self, user):
        """
        Makes the current user follow the provided user.

        Args:
            user (User): The user to be followed.
        Returns:
            None
        """
        if not self.is_following(user):
            self.following.add(user)

    def unfollow(self, user):
        """
        Makes the current user unfollow the provided user.

        Args:
            user (User): The user to be unfollowed.
        Returns:
            None
        """
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user):
        """
        Checks if the current user is following the provided user.

        Args:
            user (User): The user to check if the current user is following.
        Returns:
            bool: True if the user is being followed, False otherwise.
        """
        query = self.following.select().where(User.id == user.id)
        return db.session.scalar(query) is not None

    def followers_count(self):
        """
        Returns the count of followers for the current user.

        Returns:
            int: The number of followers.
        """
        # pylint: disable=E1102
        query = sa.select(sa.func.count()).select_from(
            self.followers.select().subquery()
        )
        return db.session.scalar(query)

    def following_count(self):
        """
        Returns the count of users the current user is following.

        Returns:
            int: The number of users being followed.
        """
        # pylint: disable=E1102
        query = sa.select(sa.func.count()).select_from(
            self.following.select().subquery()
        )
        return db.session.scalar(query)

    def following_posts(self):
        """
        Returns the posts from users that the current user follows, including their own posts.

        Returns:
            sqlalchemy.orm.Query: A query object that can be executed to retrieve the posts.
        """
        # pylint: disable=C0103
        Author = so.aliased(User)
        Follower = so.aliased(User)
        return (
            sa.select(Post)
            .join(Post.author.of_type(Author))
            .join(Author.followers.of_type(Follower), isouter=True)
            .where(
                sa.or_(
                    Follower.id == self.id,
                    Author.id == self.id,
                )
            )
            .group_by(Post)
            .order_by(Post.timestamp.desc())
        )

    def get_reset_password_token(self, expires_in=600):
        """
        Generates a reset password token for the user, which is valid for a specified time.

        Args:
            expires_in (int, optional): The expiration time in seconds for the token (default
            is 600 seconds, or 10 minutes).

        Returns:
            str: The encoded JWT token that can be used for resetting the user's password.
        """
        return jwt.encode(
            {"reset_password": self.id, "exp": time() + expires_in},
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        )

    @staticmethod
    # pylint: disable=inconsistent-return-statements
    def verify_reset_password_token(token):
        """
        Verifies the provided reset password token and retrieves the associated user.

        Args:
            token (str): The JWT token to verify, which should contain the user's ID
            for resetting the password.

        Returns:
            User or None: The User object if the token is valid, otherwise None.
        """
        # pylint: disable=redefined-builtin
        try:
            id = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )["reset_password"]
        except jwt.exceptions.InvalidTokenError as e:
            print(f"Invalid token error: {e}")
            return
        return db.session.get(User, id)


class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return [], 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        query = sa.select(cls).where(cls.id.in_(ids)).order_by(
            db.case(*when, value=cls.id))
        return db.session.scalars(query), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in db.session.scalars(sa.select(cls)):
            add_to_index(cls.__tablename__, obj)


# pylint: disable=too-few-public-methods
class Post(SearchableMixin, db.Model):
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
    language: so.Mapped[Optional[str]] = so.mapped_column(sa.String(5))
    __searchable__ = ['body']

    def __repr__(self) -> str:
        """
        Returns a string representation of the Post object.

        Returns:
            str: Astring in the format "<Post body>" for debugging.
        """
        return f"<Post {self.body}>"


# pylint: disable=W0622
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


db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)
