"""Defines the Flask application and routing for web500.
"""

import random
import string
from flask import Flask
from flask import session, render_template, redirect, url_for, abort, request

from web500.actions import AppAction
import web500.config
import web500.store as store


app = Flask(__name__)
app.config.from_object(web500.config)

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

    if session['userid'] not in store.state['rooms'][room_id]['nicknames']:
        return render_template("register_nickname.html",
                               room_id=room_id,
                               invalid_nickname=request.args.get('invalid_nickname'))
    else:
        return render_template("room.html", room_id=room_id)


@app.route('/room/<room_id>/join', methods=['POST'])
def join_room(room_id):
    """Register a nickname for a particular room.
    """
    if room_id not in store.state['rooms']:
        abort(404)
    ensure_unique_id()

    nicknames = store.state['rooms'][room_id]['nicknames']
    if request.form['nickname'] not in nicknames.values():
        store.dispatch(AppAction.set_room_nickname,
                       {'room_id': room_id,
                        'user_id': session['userid'],
                        'nickname': request.form['nickname']})
        return redirect(url_for('room', room_id=room_id))

    else:
        return redirect(url_for('room', room_id=room_id,
                                invalid_nickname=True))


@app.route('/room', methods=['POST'])
def new_room():
    """Sets up a new room and redirects the user to that room.
    """
    while True:
        new_id = ''.join(random.choice(id_selection)
                         for _ in range(room_id_length))
        if new_id not in store.state['rooms']:
            break
    store.dispatch(AppAction.new_room, {'room_id': new_id})
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

        store.dispatch(AppAction.new_user, {'user_id': new_id})
        session['userid'] = new_id
