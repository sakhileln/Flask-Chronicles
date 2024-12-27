"""
This module contains routes for the Flask application, providing the core
functionality for user authentication, profile management, and interaction
with other users (such as following and unfollowing). It includes the
following routes:

- `/index` (Home Page): Displays recent posts and allows authenticated users
  to view content.
- `/login`: Allows users to log in.
- `/logout`: Logs out the current user and redirects to the home page.
- `/register`: Registers a new user.
- `/user/<username>`: Displays the profile of the specified user along with
  their posts.
- `/edit_profile`: Allows authenticated users to edit their profile.
- `/follow/<username>`: Allows users to follow another user.
- `/unfollow/<username>`: Allows users to unfollow another user.

The module also includes a `before_request` function to update the last seen
timestamp for authenticated users.

Each route uses Flask's `render_template` to render the corresponding HTML
templates, and `flash` to display messages for user actions.
"""

# Standard library imports
from datetime import datetime, timezone
from urllib.parse import urlsplit

# Third-party imports
import sqlalchemy as sa
from flask import (
    render_template,
    flash,
    redirect,
    url_for,
    request,
    g,
    current_app
)
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from langdetect import detect, LangDetectException

# Local application imports
# pylint: disable=cyclic-import
from app import db
from app.ggl_translate import translate

# pylint: disable=cyclic-import
from app.models import User, Post

# pylint: disable=cyclic-import
from app.main.forms import (
    EditProfileForm,
    EmptyForm,
    PostForm,
)

from app.main import bp


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    """
    Route for the home page, showing recent posts.
    Only accessible by authenticated users.
    """
    form = PostForm()
    if form.validate_on_submit():
        try:
            language = detect(form.post.data)
        except LangDetectException:
            language = ''
        post = Post(body=form.post.data, author=current_user,
                    language=language)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is now live!'))
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    posts = db.paginate(
        current_user.following_posts(),
        page=page,
        per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False
    )
    next_url = url_for('main.index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template(
        'index.html',
        title=_('Home'),
        form=form,
        posts=posts.items,
        next_url=next_url,
        prev_url=prev_url
    )



@bp.route("/user/<username>")
@login_required
def user(username):
    """
    Route to view a user's profile. Shows the user's posts.
    Only accessible by authenticated users.
    """
    # pylint: disable=redefined-outer-name
    user = db.first_or_404(sa.select(User).where(User.username == username))
    page = request.args.get('page', 1, type=int)
    query = user.posts.select().order_by(Post.timestamp.desc())
    posts = db.paginate(
        query,
        page=page,
        per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False
    )
    next_url = url_for(
        'main.user',
        username=user.username,
        page=posts.next_num
    ) if posts.has_next else None
    prev_url = url_for(
        'main.user',
        username=user.username,
        page=posts.prev_num
    ) if posts.has_prev else None
    form = EmptyForm()
    return render_template(
        'user.html',
        user=user,
        posts=posts.items,
        next_url=next_url,
        prev_url=prev_url,
        form=form
    )


@bp.before_request
def before_request():
    """
    A function that runs before every request. Updates the current user's
    'last_seen' timestamp if the user is authenticated.
    """
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()
    g.locale = str(get_locale())


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """
    Route for editing the current user's profile information.
    Only accessible by authenticated users.
    """
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template(
        'edit_profile.html',
        title=_('Edit Profile'),
        form=form
    )


@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    """
    Route for following another user. Only accessible by authenticated users.
    """
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username))
        if user is None:
            flash(_('User %(username)s not found.', username=username))
            return redirect(url_for('main.index'))
        if user == current_user:
            flash(_('You cannot follow yourself!'))
            return redirect(url_for('main.user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(_('You are following %(username)s!', username=username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))


@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    """
    Route for unfollowing another user. Only accessible by authenticated users.
    """
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username))
        if user is None:
            flash(_('User %(username)s not found.', username=username))
            return redirect(url_for('main.index'))
        if user == current_user:
            flash(_('You cannot unfollow yourself!'))
            return redirect(url_for('main.user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(_('You are not following %(username)s.', username=username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))


@bp.route("/explore")
@login_required
def explore():
    """
    Route for exploring all posts in descending order of their timestamp.
    Pagination:
    - The page number is obtained from the query parameter (`page`), defaulting to page 1.
    - The number of posts per page is controlled by the configuration setting `POSTS_PER_PAGE`.
    - The `next_url` and `prev_url` are generated to navigate between pages, based on
        the current page.

    Returns:
        A rendered template (`index.html`) displaying the posts for the current page, along with
        navigation links for previous and next pages if applicable.
    """
    page = request.args.get('page', 1, type=int)
    query = sa.select(Post).order_by(Post.timestamp.desc())
    posts = db.paginate(
        query,
        page=page,
        per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False
    )
    next_url = url_for('main.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template(
        'index.html',
        title=_('Explore'),
        posts=posts.items,
        next_url=next_url,
        prev_url=prev_url
    )

@bp.route("/translate", methods=["POST"])
@login_required
def translate_text():
    """
    Handle translation requests.

    This route accepts a POST request containing JSON data with the text to be translated,
    the source language, and the destination language. It requires the user to be logged in.
    The function uses the `translate` function to perform the translation and returns
    the translated text in JSON format.

    Example:
    POST /translate
    {
        "text": "Hello, world!",
        "source_language": "en",
        "dest_language": "es"
    }

    Response:
    {
        "text": "¡Hola, mundo!"
    }
    """
    data = request.get_json()
    return {
        "text": translate(data["text"], data["source_language"], data["dest_language"])
    }
