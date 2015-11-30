"""Chat logic for web500.  Implements a websocket handler for communication.
"""

import flask.sessions
import json
import tornado.web
from tornado.websocket import WebSocketHandler
from itsdangerous import URLSafeTimedSerializer

from web500.app import app


def total_seconds(td):
    """Returns the total seconds from a timedelta object.  Copied from
    ``flask.helpers``.
    """
    return td.days * 60 * 60 * 24 + td.seconds


class ChatSocketHandler(WebSocketHandler):
    """Implements an interface for communication with other users via chat.

    Cookies from the corresponding Flask session are inspected during the
    initial handshake, and sessions with invalid cookies are dropped.
    """

    def get_flask_session(self):
        """Unencrypts a Flask encrypted session cookie.

        Based on code in ``flask.sessions``.
        """
        flaskSessionInterface = flask.sessions.SecureCookieSessionInterface()
        cookieSerializer = flaskSessionInterface.get_signing_serializer(app)
        cookie = self.get_cookie(app.session_cookie_name)
        max_age = total_seconds(app.permanent_session_lifetime)
        return cookieSerializer.loads(cookie, max_age=max_age)

    @tornado.web.asynchronous
    def get(self, *args, **kwargs):
        cookie_data = self.get_flask_session()
        if "username" not in cookie_data:
            app.logger.warning("Unauthorised user tried to connect to chat")
            return
        super(ChatSocketHandler, self).get(*args, **kwargs)

    def open(self):
        print("WebSocket opened")

    def on_message(self, message):
        print(message)
        self.write_message(message)

    def on_close(self):
        print("WebSocket closed")
