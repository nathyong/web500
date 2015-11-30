"""Module for dealing with database connections.
"""

import sqlite3
from flask import g
from web500.app import app

def get_db():
    """Get the current copy of the database.
    """
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE_URI'])
    return db

def update_db(query, args=()):
    """Update the database in one go.
    """
    get_db().execute(query, args)
    get_db().commit()

def query_db(query, args=(), one=False):
    """Query the database in one go.
    Method from Flask quickstart.
    """
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.teardown_appcontext
def close_connection(exception):
    """Clean up the connection to the database.
    """
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
