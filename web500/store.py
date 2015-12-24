"""Defines the data stores for the web500 app.
"""

state = {}

_handlers = []
_listeners = []

def dispatch(action):
    """Dispatch an action on the store, updating its contents and triggering
    possible updates.
    """
    for fn in _handlers:
        globals()['state'] = fn(action)

    for fn in _listeners:
        fn()

def subscribe(listener):
    """Add a callback to be triggered on a state update.  Returns a function
    that unsubscribes the listener.
    """
    _listeners.append(listener)

def register_handler(handler):
    """Add a _pure_ handler to the list of handlers.
    """
    _handlers.insert(0, handler)
