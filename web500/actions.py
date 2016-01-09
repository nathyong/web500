"""Defines the datastore actions and handlers for web500.

For the shape of the data, refer to `_initial_state` and `_initial_room_state`.
"""

import functools
from copy import deepcopy
from enum import Enum
from schema import Schema

from web500.store import handle

_initial_state = {'userids': set(),
                  'rooms': {}            # room_id : room_state
                 }
_initial_room_state = {'nicknames': {},  # user_id : nickname
                       'gamedata': {},   # TBD
                       'messages': [],   # [{messages}]
                       'online_users': set()
                      }

class AppAction(Enum):
    """Enumeration of all possible actions in web500.
    """
    init = Schema({})
    new_user = Schema({'user_id': str})
    new_room = Schema({'room_id': str})
    join_room = Schema({'room_id': str, 'user_id': str})
    leave_room = Schema({'room_id': str, 'user_id': str})
    set_room_nickname = Schema({'room_id': str,
                                'user_id': str,
                                'nickname': str})
    message_room = Schema({'room_id': str,
                           'sender_id': str,
                           'message': str})

    def __init__(self, schema):
        self.schema = schema


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
    store['userids'].add(data['user_id'])
    return store


@handle(AppAction.new_room)
@pure_arguments
def new_room(data, store):
    """Add a new room to the store.
    """
    store['rooms'][data['room_id']] = _initial_room_state
    return store


@handle(AppAction.join_room)
@pure_arguments
def join_room(data, store):
    """Adds a user to a room, associating it with a room-specific nickname.
    """
    store['rooms'][data['room_id']]['online_users'].add(data['user_id'])
    return store


@handle(AppAction.message_room)
@pure_arguments
def message_room(data, store):
    """Adds a message to the room message log.
    """
    sender = store['rooms'][data['room_id']]['nicknames'][data['sender_id']]
    message = {'from': sender,
               'messsage': data['message']}
    store['rooms'][data['room_id']]['messages'].append(message)
    return store


@handle(AppAction.leave_room)
@pure_arguments
def leave_room(data, store):
    """Removes a user from a room.
    """
    store['rooms'][data['room_id']]['online_users'].remove(data['user_id'])
    return store


@handle(AppAction.set_room_nickname)
@pure_arguments
def set_room_nickname(data, store):
    """Binds a user to a nickname for a particular room.
    """
    store['rooms'][data['room_id']]['nicknames'][data['user_id']] = data['nickname']
    return store
