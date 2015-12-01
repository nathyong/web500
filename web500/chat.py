"""Chat logic for web500.  Implements a websocket handler for communication.
"""

import flask.sessions
import json
import tornado.web
from flask import Markup
from tornado.websocket import WebSocketHandler
from itsdangerous import URLSafeTimedSerializer

from web500.app import app


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

    .. attribute:: connected_sessions

       A dictionary of format {user: socket}, used to represent the users who
       are connected to the chat server.
    """

    connected_sessions = {}

    def send_user_list(self):
        """Sends the list of users to all connected users.
        """
        user_list_response = {"act": "users",
                              "users": list(self.connected_sessions.keys())}
        for sock in self.connected_sessions.values():
            sock.write_message(user_list_response)


    def get_flask_session(self):
        """Unencrypts a Flask encrypted session cookie.

        Based on code in ``flask.sessions``.
        """
        cookie = self.get_cookie(app.session_cookie_name)
        max_age = total_seconds(app.permanent_session_lifetime)
        return cookieSerializer.loads(cookie, max_age=max_age)

    @tornado.web.asynchronous
    def get(self, *args, **kwargs):
        session = self.get_flask_session()
        if "username" not in session:
            app.logger.warning("chat: unauthorised user tried to connect to chat")
            return
        super(ChatSocketHandler, self).get(*args, **kwargs)

    def open(self):
        session = self.get_flask_session()
        self.connected_sessions[session["username"]] = self
        app.logger.info("chat: socket connection opened")
        self.send_user_list()

    def on_message(self, message):
        contents = json.loads(message)
        session = self.get_flask_session()
        response = {"act": "chat",
                    "from": session["username"],
                    "message": Markup.escape(contents["message"])}
        for sock in self.connected_sessions.values():
            sock.write_message(response)

    def on_close(self):
        session = self.get_flask_session()
        del self.connected_sessions[session["username"]]
        app.logger.info("chat: socket connection closed")
        self.send_user_list()
