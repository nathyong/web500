"""Defines the datastore handlers for web500.
"""

from web500.actions import AppAction
from web500.store import register_handler

def handle_init(_, old_store):
    """Initialise the database on an init event.
    """
    store = dict(old_store)
    store['userids'] = set()
    return store

def handle_new_user(data, old_store):
    """Add a new user to the store.
    """
    store = dict(old_store)
    store['userids'].add(data['id'])
    return store

register_handler(AppAction.init, handle_init)
register_handler(AppAction.new_user, handle_new_user)
