"""Defines different Flask routes for the actual server for web500.
"""

from flask import render_template, session, request, redirect, url_for
from web500.app import app
from web500.db import query_db, update_db
from web500.room import get_room

@app.route('/')
def index():
    """Handles the index page"""
    if 'username' not in session:
        return redirect(url_for("login"))
    return render_template("index.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    """Authenticates new users"""
    if 'username' in session:
        return redirect(url_for("index"))

    if request.method == "POST":
        if not query_db("select * from users where username = ?",
                        [request.form['username']]):
            session['username'] = request.form['username']
            update_db("insert into users (username) values (?)",
                      [request.form['username']])
            return redirect(url_for("index"))
        else:
            return render_template("login.html", invalid_login=True)
    else:
        return render_template("login.html")

@app.route('/logout')
def logout():
    """Unsets the currently logged-in session"""
    session.pop("username", None)
    return redirect(url_for("index"))

@app.route('/room/<room_id>')
def room(room_id):
    """Allows users to connect to a room together, to chat and play a game of
    500.
    """
    return get_room(room_id).handle_route()

@app.route('/room', methods=["POST"])
def new_room():
    """Sets up a new room and redirects the user to that room.
    """
    return redirect(url_for("room", room_id=get_room().room_id))
