"""Defines the datastore actions and handlers for web500.

For the shape of the data, refer to `_initial_state` and `_initial_room_state`.
"""

import functools
from copy import deepcopy
from enum import Enum

from web500.store import handle

_initial_state = {'userids': set(),
                  'rooms': {}           # room_id : room_state
                 }
_initial_room_state = {'users': {},     # user_id : nickname
                       'gamedata': {},  # TBD
                       'messages': []   # [{messages}]
                      }

class AppAction(Enum):
    """Enumeration of all possible actions in web500.
    """
    init = 'init'
    new_user = 'new_user'
    new_room = 'new_room'
    join_room = 'join_room'
    leave_room = 'leave_room'
    message_room = 'message_room'


def pure_arguments(f):
    """Convenient decorator to deepcopy all arguments of a function before it is
    called.
    """
    #pylint: disable=missing-docstring
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        pure_args = (deepcopy(arg) for arg in args)
        pure_kwargs = {k: deepcopy(v) for k, v in kwargs.items()}
        return f(*pure_args, **pure_kwargs)
    return wrapper


@handle(AppAction.init)
@pure_arguments
def init(*_):
    """Initialise the database on an init event.
    """
    return _initial_state


@handle(AppAction.new_user)
@pure_arguments
def new_user(data, store):
    """Add a new user to the store.
    """
    store['userids'].add(data['id'])
    return store


@handle(AppAction.new_room)
@pure_arguments
def new_room(data, store):
    """Add a new room to the store.
    """
    store['rooms'][data['id']] = _initial_room_state
    return store


@handle(AppAction.join_room)
@pure_arguments
def join_room(data, store):
    """Adds a user to a room, associating it with a room-specific nickname.
    """
    store['rooms'][data['room']]['users'][data['user']] = 'some_nickname'
    return store


@handle(AppAction.message_room)
@pure_arguments
def message_room(data, store):
    """Adds a message to the room message log.
    """
    message = {'from': data['from'],
               'messsage': data['message']}
    store['rooms'][data['room']]['messages'].append(message)
    return store


@handle(AppAction.leave_room)
@pure_arguments
def leave_room(data, store):
    """Removes a user from a room.
    """
    del store['rooms'][data['room']]['users'][data['user']]
    return store
