"""Defines different Flask routes for the actual server for web500.
"""

from flask import Flask, render_template, session, request, redirect, url_for
from web500.app import app
from web500.db import query_db

@app.route('/')
def index():
    """Handles the index page"""
    if 'username' not in session:
        return redirect(url_for("login"))
    return render_template("index.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    """Authenticates new users"""
    if request.method == "POST":
        if not query_db("select * from users where username = ?",
                        request.form['username']):
            session['username'] = request.form['username']
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
