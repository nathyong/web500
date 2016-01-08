"""Defines different Flask routes for the actual server for web500.
"""

from flask import session, render_template, redirect, url_for, abort
import random
import string

from web500.actions import AppAction
from web500.app import app
import web500.store as store

id_length = 32
room_id_length = 5
id_selection = string.ascii_lowercase + string.digits

@app.route('/')
def index():
    """Handles the index page.
    """
    ensure_unique_id()
    return render_template("index.html")


@app.route('/room/<room_id>')
def room(room_id):
    """Allows users to connect to a particular room.
    """
    if room_id not in store.state['rooms']:
        abort(404)
    ensure_unique_id()
    return render_template("room.html", room_id=room_id)


@app.route('/room', methods=['POST'])
def new_room():
    """Sets up a new room and redirects the user to that room.
    """
    while True:
        new_id = ''.join(random.choice(id_selection)
                         for _ in range(room_id_length))
        if new_id not in store.state['rooms']:
            break
    store.dispatch(AppAction.new_room, {'id': new_id})
    return redirect(url_for('room', room_id=new_id))


def ensure_unique_id():
    """Sets an app-wide unique user ID for a user if they do not already have
    one in their session.
    """
    if 'userid' not in session or session['userid'] not in store.state['userids']:
        while True:
            new_id = ''.join(random.choice(id_selection) for _ in range(id_length))
            if new_id not in store.state['userids']:
                break

        store.dispatch(AppAction.new_user, {'id': new_id})
        session['userid'] = new_id
