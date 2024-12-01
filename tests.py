"""
Module-level docstring for testing the user model and related functionalities
Test suite for the User model in the application.

This suite tests the following functionalities:
- Password hashing and checking
- User avatar generation
- Following and unfollowing other users
- Fetching posts of followed users
"""

import os
from datetime import datetime, timezone, timedelta
import unittest
from app import app, db
from app.models import User, Post


os.environ["DATABASE_URL"] = "sqlite://"


class UserModelCase(unittest.TestCase):
    """
    Test case for the User model that covers operations such as password hashing,
    avatar generation, and the following functionality (following/unfollowing users,
    posts from followed users).

    Methods:
    setUp() -- Initializes app context and database.
    tearDown() -- Cleans up database and app context.
    test_password_hashing() -- Tests password hashing and checking.
    test_avatar() -- Tests avatar URL generation.
    test_follow() -- Tests follow and unfollow functionality.
    test_follow_posts() -- Tests fetching posts of followed users.
    """

    def setUp(self):
        """
        Set up the application context and create all tables in the database.
        This method is called before every test method in the class.
        """
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """
        Tear down the application context and drop all tables in the database.
        This method is called after every test method in the class.
        """
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        """
        Test the password hashing functionality.

        Verifies that:
        - A password is hashed correctly using `set_password`.
        - The password can be checked using `check_password`.
        """
        u = User(username="zothi", email="zothi@example.com")
        u.set_password("cat")
        self.assertFalse(u.check_password("dog"))
        self.assertTrue(u.check_password("cat"))

    def test_avatar(self):
        """
        Test the avatar URL generation for a user.

        Verifies that:
        - The avatar URL is generated correctly based on the user's email.
        """
        u = User(username="sakhile", email="sakhile@example.com")
        self.assertEqual(
            u.avatar(128),
            (
                "https://www.gravatar.com/avatar/"
                "8230f8c59bac6b3d0d6aa3d70e1638c4"
                "?d=identicon&s=128'"
            ),
        )

    def test_follow(self):
        """
        Test the follow and unfollow functionality between users.

        Verifies that:
        - Users can follow and unfollow each other.
        - The following and follower counts are updated correctly.
        - The `is_following` and `following_count` methods work as expected.
        """
        u1 = User(username="sakhi", email="sakhi@example.com")
        u2 = User(username="zethe", email="zethe@example.com")
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        following = db.session.scalars(u1.following.select()).all()
        followers = db.session.scalars(u2.followers.select()).all()
        self.assertEqual(following, [])
        self.assertEqual(followers, [])

        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.following_count(), 1)
        self.assertEqual(u2.followers_count(), 1)
        u1_following = db.session.scalars(u1.following.select()).all()
        u2_followers = db.session.scalars(u2.followers.select()).all()
        self.assertEqual(u1_following[0].username, "zethe")
        self.assertEqual(u2_followers[0].username, "sakhi")

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.following_count(), 0)
        self.assertEqual(u2.followers_count(), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)