"""A class, `Room`, which implements handlers for both chat and socket
interfaces for a particular room, where people can get together and chat or play
a game of 500 together.

Implements a factory/singleton function, `get_room`, which can be used to get
references to rooms.
"""

import json
import random
import string
from flask import render_template, session, abort, Markup

_rooms = {}
id_length = 5

class Room(object):
    """Represents a room, where people can do things together.  Conceptually
    this class ties together the page rendering, chat and game services of
    a particular room.

    .. attribute:: room_id

       A string of `web500.room.id_length` lowercase letters and digits
       representing a unique ID of a room.  Used in the URL of the room, as well
       as to distinguish different rooms.

    .. attribute:: chat_sockets

       A dictionary of format `{socket: user}`, used to represent the users who
       are connected to a particular room via chat.
    """

    def __init__(self, room_id):
        self.room_id = room_id
        self.chat_sockets = {}

    def handle_route(self):
        """Returns webpage contents suitable for passing to a Flask route
        handler.

        Needs to be called inside a Flask context.
        """
        return render_template("room.html", room_id=self.room_id)

    def add_chat_connection(self, socket, name):
        """Register a new chat socket connection to this room, associated with
        a particular nickname for a user.
        """
        self.chat_sockets[socket] = name
        self.send_user_list()

    def handle_chat_message(self, message, name):
        """Relay an incoming message from a particular user to all users.
        """
        contents = json.loads(message)
        response = {"act": "chat",
                    "from": name,
                    "message": Markup.escape(contents["message"])}
        for sock in self.chat_sockets:
            sock.write_message(response)

    def remove_chat_connection(self, socket):
        """Remove a socket from the list of connected sockets.
        """
        del self.chat_sockets[socket]
        self.send_user_list()

    def send_user_list(self):
        """Sends the list of users to all connected websockets for this
        particular room.
        """
        user_list_response = {"act": "users",
                              "users": list(set(self.chat_sockets.values()))}
        for sock in self.chat_sockets:
            sock.write_message(user_list_response)


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
