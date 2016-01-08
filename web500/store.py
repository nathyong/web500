"""Defines the data store for the web500 app.
"""

from datadiff import diff
from pprint import pprint

state = {}
_last_state = {}

_handlers = {}
_listeners = []

_logger = None

def dispatch(action, data):
    """Dispatch an action on the store, updating its contents and triggering
    possible updates.

    :arg action: the type of action.  Can be implemented with an enum or just
        a string.

    :arg data: the data to pass to the handler.  Can be implemented with a
        dict.
    """
    global state
    global _last_state
    _log_debug('Dispatch: {}: {}'.format(action, data))
    _last_state = state
    state = _handlers[action](data, state)
    print(diff(_last_state, state))

    for fn in _listeners:
        fn()

def subscribe(listener):
    """Add a callback to be triggered on a state update.  Returns a function
    that unsubscribes the listener.
    """
    _listeners.append(listener)
    return lambda: _listeners.remove(listener)

def register_handler(action, handler):
    """Add a _pure_ handler to the list of handlers.
    """
    _handlers[action] = handler

def handle(action):
    """Convenient decorator for registering pure handlers.
    """
    return lambda f: register_handler(action, f)

def changed(accessor):
    """Determine if a subset of the state (accessed by the provided function)
    has changed since the last dispatch.
    """
    return accessor(state) != accessor(_last_state)

def _log_debug(msg):
    """Log a message on the debug level.
    """
    if _logger is not None:
        _logger.debug(msg)
