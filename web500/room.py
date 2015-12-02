"""A class, `Room`, which implements handlers for both chat and socket
interfaces for a particular room, where people can get together and chat or play
a game of 500 together.

Implements a factory/singleton function, `get_room`, which can be used to get
references to rooms.
"""

import string
import random
from flask import render_template, session, abort

_rooms = {}
id_length = 5


#pylint: disable=R0921
class Room(object):
    """Represents a room, where people can do things together.  Conceptually
    this class ties together the page rendering, chat and game services of
    a particular room.
    """

    def __init__(self, room_id):
        self.room_id = room_id

    def handle_route(self):
        """Returns webpage contents suitable for passing to a Flask route
        handler.

        Needs to be called inside a Flask context.
        """
        return render_template("room.html", room_id=self.room_id)

    def handle_chat(self):
        raise NotImplementedError


def generate_room_id():
    """Returns random alphanumeric strings of length `web500.room.id_length`.
    """
    selection = string.ascii_lowercase + string.digits
    while True:
        new_id = ''.join(random.choice(selection) for _ in range(id_length))
        if new_id not in _rooms:
            return new_id


def get_room(room_id=None):
    """Either request a room if it exists, or create a room if necessary.

    :arg room_id: is the room ID to retrieve.  If this is ``None``, then return
        a reference to a new room.
    """
    if room_id is None:
        r = Room(generate_room_id())
        _rooms[r.room_id] = r
        return r
    else:
        try:
            return _rooms[room_id]
        except KeyError:
            abort(404)
