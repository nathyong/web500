"""Application and presentation logic for web500.
"""

from flask import Flask, render_template, session, request, redirect, url_for
import web500.config

app = Flask(__name__)
app.secret_key = web500.config.settings['secret_key']


@app.route('/')
def index():
    """Handles the index page"""
    if 'username' not in session:
        return render_template("login.html")
    return render_template("index.html")

@app.route('/login', methods=["POST"])
def login():
    """Authenticates new users"""
    session['username'] = request.form['username']
    return redirect(url_for("index"))

@app.route('/logout')
def logout():
    """Unsets the currently logged-in session"""
    session.pop("username", None)
    return redirect(url_for("index"))
