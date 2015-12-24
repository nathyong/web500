"""Defines different Flask routes for the actual server for web500.
"""

from flask import session, render_template
import random
import string

from web500.actions import AppAction
from web500.app import app
import web500.store as store

id_length = 32

@app.route('/')
def index():
    """Handles the index page.
    """
    ensure_unique_id()
    return render_template("index.html")


def ensure_unique_id():
    """Sets an app-wide unique user ID for a user if they do not already have
    one in their session.
    """
    if 'userid' not in session or session['userid'] not in store.state['userids']:
        selection = string.ascii_lowercase + string.digits
        while True:
            new_id = ''.join(random.choice(selection) for _ in range(id_length))
            if new_id not in store.state['userids']:
                break

        store.dispatch(AppAction.new_user, {'id': new_id})
        session['userid'] = new_id
