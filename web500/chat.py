"""Chat logic for web500.  Implements a websocket handler for communication.
"""

import flask.sessions
import tornado.web
from tornado.websocket import WebSocketHandler
from itsdangerous import URLSafeTimedSerializer

from web500.app import app
from web500.room import get_room


flaskSessionInterface = flask.sessions.SecureCookieSessionInterface()
cookieSerializer = flaskSessionInterface.get_signing_serializer(app)

def total_seconds(td):
    """Returns the total seconds from a timedelta object.  Copied from
    ``flask.helpers``.
    """
    return td.days * 60 * 60 * 24 + td.seconds


class ChatSocketHandler(WebSocketHandler):
    """Implements an interface for communication with other users via chat.

    Cookies from the corresponding Flask session are inspected during the
    initial handshake, and sessions with invalid cookies are dropped.

    .. attribute:: room

       A reference to the `web500.room.Room` which this websocket connection is
       associated to.

    .. attribute:: user

       The nickname of the user who is connected through this socket.
    """

    def get_flask_session(self):
        """Unencrypts a Flask encrypted session cookie.

        Based on code in ``flask.sessions``.
        """
        cookie = self.get_cookie(app.session_cookie_name)
        max_age = total_seconds(app.permanent_session_lifetime)
        return cookieSerializer.loads(cookie, max_age=max_age)

    def __init__(self, *args, **kwargs):
        self.connected_sessions = {}
        self.room = None
        self.user = None
        super().__init__(*args, **kwargs)

    @tornado.web.asynchronous
    def get(self, room_id=None, *args, **kwargs):
        session = self.get_flask_session()
        if "username" not in session:
            app.logger.warning("chat: unauthorised user tried to connect to chat")
            return
        self.room = get_room(room_id)
        self.user = session["username"]
        super().get(*args, **kwargs)

    def open(self):
        self.room.add_chat_connection(self, self.user)
        app.logger.info("chat: socket connection opened at {}".format(self.room.room_id))

    def on_message(self, message):
        self.room.handle_chat_message(message, self.user)

    def on_close(self):
        self.room.remove_chat_connection(self)
        app.logger.info("chat: socket connection closed at {}".format(self.room.room_id))
