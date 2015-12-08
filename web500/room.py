"""A class, `Room`, which implements handlers for the socket interfaces for
a particular room, where people can get together and chat or play a game of 500
together.

Implements a factory/singleton function, `get_room`, which can be used to get
references to rooms.
"""

import json
import random
import string
from flask import render_template, session, abort, Markup

from web500.app import app

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

    .. attribute:: sockets

       A dictionary of format `{socket: user}`, used to represent the users who
       are connected to a particular room via chat.
    """

    def __init__(self, room_id):
        self.room_id = room_id
        self.sockets = {}

    def handle_route(self):
        """Returns webpage contents suitable for passing to a Flask route
        handler.

        Needs to be called inside a Flask context.
        """
        return render_template("room.html", room_id=self.room_id)

    def add_connection(self, socket, name):
        """Register a new chat socket connection to this room, associated with
        a particular nickname for a user.
        """
        self.sockets[socket] = name
        self.send_user_list()

    def handle_message(self, message, name):
        """Handle an incoming message based on the action encoded in the
        message.  Uses runtime reflection/dispatch to determine what to do.
        """
        contents = json.loads(message)
        try:
            function_name = "_handle_" + contents["act"]
            dispatch_function = getattr(self, function_name)
            dispatch_function(contents, name)
        except KeyError:
            app.logger.warning("malformed message (no action): {}", message)
        except AttributeError:
            app.logger.warning("malformed message (bad action): {}", message)

    def _handle_chat(self, contents, name):
        """Process a chat message by relaying it to all other connected users.
        """
        response = {"act": "chat",
                    "from": name,
                    "message": Markup.escape(contents["message"])}
        broadcast(response, self.sockets)

    def remove_connection(self, socket):
        """Remove a socket from the list of connected sockets.
        """
        del self.sockets[socket]
        self.send_user_list()

    def send_user_list(self):
        """Sends the list of users to all connected websockets for this
        particular room.
        """
        user_list_response = {"act": "users",
                              "users": list(set(self.sockets.values()))}
        broadcast(user_list_response, self.sockets)


def broadcast(contents, sockets):
    """Push a message out over possibly many sockets.

    :arg contents: the message as a dictionary, or something else that can be
        sent with `tornado.websocket.WebSocketHandler.write_message`.

    :arg sockets: an iterable collection of
        `tornado.websocket.WebSocketHandler` objects.
    """
    for sock in sockets:
        sock.write_message(contents)


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
