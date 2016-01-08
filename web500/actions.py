"""Defines the datastore actions and handlers for web500.

The data store pattern looks a bit like this currently:
```
{'userids': {},
 'rooms': {id: {'users': {userid: nickname},
                'gamedata': data,
                'messages': [message]
               }
          }
}
```
"""

from copy import deepcopy
from enum import Enum
from web500.store import handle

class AppAction(Enum):
    """Enumeration of all possible actions in web500.
    """
    init = 'init'
    new_user = 'new_user'
    new_room = 'new_room'
    join_room = 'join_room'
    leave_room = 'leave_room'
    message_room = 'message_room'


@handle(AppAction.init)
def init(*_):
    """Initialise the database on an init event.
    """
    store = {'userids': set(),
             'rooms': {}}
    return store


@handle(AppAction.new_user)
def new_user(data, old_store):
    """Add a new user to the store.
    """
    store = deepcopy(old_store)
    store['userids'].add(data['id'])
    return store


@handle(AppAction.new_room)
def new_room(data, old_store):
    """Add a new room to the store.
    """
    store = deepcopy(old_store)
    store['rooms'][data['id']] = {'users': {},
                                  'gamedata': {},
                                  'messages': []}
    return store


@handle(AppAction.join_room)
def join_room(data, old_store):
    """Adds a user to a room, associating it with a room-specific nickname.
    """
    store = deepcopy(old_store)
    store['rooms'][data['room']]['users'][data['user']] = 'some_nickname'
    return store


@handle(AppAction.message_room)
def message_room(data, old_store):
    """Adds a message to the room message log.
    """
    store = deepcopy(old_store)
    message = {'from': data['from'],
               'messsage': data['message']}
    store['rooms'][data['room']]['messages'].append(message)
    return store


@handle(AppAction.leave_room)
def leave_room(data, old_store):
    """Removes a user from a room.
    """
    store = deepcopy(old_store)
    del store['rooms'][data['room']]['users'][data['user']]
    return store
