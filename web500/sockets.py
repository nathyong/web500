"""Communication with the client for web500.  Implements a websocket handler.
"""

import flask.sessions
import tornado.web
from tornado.websocket import WebSocketHandler
from itsdangerous import URLSafeTimedSerializer

from web500.app import app
from web500.actions import AppAction
import web500.store as store


flaskSessionInterface = flask.sessions.SecureCookieSessionInterface()
cookieSerializer = flaskSessionInterface.get_signing_serializer(app)

def total_seconds(td):
    """Returns the total seconds from a timedelta object.  Copied from
    ``flask.helpers``.
    """
    return td.days * 60 * 60 * 24 + td.seconds


class GameSocketHandler(WebSocketHandler):
    """Implements an interface for communication with other users, and for
    facilitating the game itself.

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
    def get(self, room_id, *args, **kwargs):
        session = self.get_flask_session()
        if 'userid' not in session:
            app.logger.warning("unauthorised user tried to connect via socket")
            return
        self.room = room_id
        self.user = session['userid']
        super().get(*args, **kwargs)

    def open(self):
        store.dispatch(AppAction.join_room, {'room': self.room,
                                             'user': self.user})
        def _react_messages(unconditional=False):
            access_messages = lambda s: s['rooms'][self.room]['messages']
            if store.changed(access_messages) or unconditional:
                self.write_message({'messages': access_messages(store.state)})

            access_users = lambda s: s['rooms'][self.room]['users']
            if store.changed(access_users) or unconditional:
                self.write_message({'users': access_users(store.state)})

        self.listener = store.subscribe(_react_messages)
        _react_messages(unconditional=True)
        app.logger.info("socket connection opened at {}".format(self.room))

    def on_message(self, message):
        store.dispatch(AppAction.message_room, {'room': self.room,
                                                'from': self.user,
                                                'message': message})

    def on_close(self):
        self.listener()
        store.dispatch(AppAction.leave_room, {'room': self.room,
                                              'user': self.user})
        app.logger.info("socket connection closed at {}".format(self.room))
