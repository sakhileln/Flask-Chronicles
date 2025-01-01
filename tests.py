"""
Module-level docstring for testing the user model and related functionalities
Test suite for the User model in the application.

This suite tests the following functionalities:
- Password hashing and checking
- User avatar generation
- Following and unfollowing other users
- Fetching posts of followed users
"""

# pylint: disable=wrong-import-position
from datetime import datetime, timezone, timedelta
import unittest
from app import create_app, db
from app.models import User, Post
from config import Config


# pylint: disable=too-few-public-methods
class TestConfig(Config):
    """
    Test configuration class for the application.

    This class inherits from the base Config class and is used to set up
    the testing environment. It enables testing mode and configures
    SQLite as the database URI for testing purposes.
    """

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    ELASTICSEARCH_URL = None


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
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
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

    def test_follow_posts(self):
        """
        Test retrieving posts from followed users.

        Verifies that:
        - A user sees posts from users they are following.
        - The posts are returned in the correct order based on timestamp.
        """
        # create four users
        u1 = User(username="sakhi", email="sakhi@example.com")
        u2 = User(username="zethe", email="zethe@example.com")
        u3 = User(username="zothi", email="zothi@example.com")
        u4 = User(username="no", email="no@example.com")
        db.session.add_all([u1, u2, u3, u4])

        # create four posts
        now = datetime.now(timezone.utc)
        p1 = Post(
            body="post from sakhi",
            author=u1,
            timestamp=now + timedelta(seconds=1),
        )
        p2 = Post(
            body="post from zethe",
            author=u2,
            timestamp=now + timedelta(seconds=4),
        )
        p3 = Post(
            body="post from zothi",
            author=u3,
            timestamp=now + timedelta(seconds=3),
        )
        p4 = Post(
            body="post from no",
            author=u4,
            timestamp=now + timedelta(seconds=2),
        )
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        # setup the followers
        u1.follow(u2)  # sakhi follows zethe
        u1.follow(u4)  # sakhi follows no
        u2.follow(u3)  # zethe follows zothi
        u3.follow(u4)  # zothi follows no
        db.session.commit()

        # check the following posts of each user
        f1 = db.session.scalars(u1.following_posts()).all()
        f2 = db.session.scalars(u2.following_posts()).all()
        f3 = db.session.scalars(u3.following_posts()).all()
        f4 = db.session.scalars(u4.following_posts()).all()
        self.assertEqual(f1, [p2, p4, p1])
        self.assertEqual(f2, [p2, p3])
        self.assertEqual(f3, [p3, p4])
        self.assertEqual(f4, [p4])


if __name__ == "__main__":
    unittest.main(verbosity=2)
