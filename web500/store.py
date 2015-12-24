"""Defines the data store for the web500 app.
"""

state = {}

_handlers = {}
_listeners = []

_logger = None

def dispatch(action, data):
    """Dispatch an action on the store, updating its contents and triggering
    possible updates.
    """
    _log_debug('Dispatch: {}: {}'.format(action, data))
    globals()['state'] = _handlers[action](data, state)

    for fn in _listeners:
        fn()

def subscribe(listener):
    """Add a callback to be triggered on a state update.  Returns a function
    that unsubscribes the listener.
    """
    _listeners.append(listener)

def register_handler(action, handler):
    """Add a _pure_ handler to the list of handlers.
    """
    _handlers[action] = handler

def _log_debug(msg):
    """Log a message on the debug level.
    """
    if _logger is not None:
        _logger.debug(msg)
