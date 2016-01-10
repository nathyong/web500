"""Communication with the client for web500.  Implements a websocket handler.
"""

import flask.sessions
import json
import tornado.web
from datetime import datetime
from tornado.websocket import WebSocketHandler

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

       The ID of the room that this connection is associated to.

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
        self.listener = None
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
        store.dispatch(AppAction.join_room, {'room_id': self.room,
                                             'user_id': self.user})

        def _react_messages(unconditional=False):
            """Send messages when the internal state changes.
            """
            access_messages = lambda s: s['rooms'][self.room]['messages']
            if store.changed(access_messages) or unconditional:
                messages = [{'from': m['from'],
                             'text': m['text'],
                             'time': m['time'].isoformat()}
                            for m in access_messages(store.state)]
                self.write_message({
                    'act': 'chat',
                    'data': messages
                })

            access_users = lambda s: s['rooms'][self.room]['online_users']
            if store.changed(access_users) or unconditional:
                nicknames = store.state['rooms'][self.room]['nicknames']
                online_nicks = [nicknames[userid]
                                for userid in access_users(store.state)]
                response = {'act': 'users', 'users': online_nicks}
                self.write_message(response)

        self.write_message({
            'act': 'notice',
            'data': {'from': 'chatbot',
                     'text': 'Connected to the chat server! Play nice!',
                     'time': datetime.now().isoformat()}})

        self.listener = store.subscribe(_react_messages)
        _react_messages(unconditional=True)

    def on_message(self, message):
        message = json.loads(message)
        assert message['act']
        assert message['data']
        if message['act'] == 'chat':
            store.dispatch(AppAction.message_room, {
                'room_id': self.room,
                'sender_id': self.user,
                'text': message['data'],
                'time': datetime.now()})
        else:
            app.logger.error('Unexpected message: {}'.format(message))

    def on_close(self):
        self.listener()
        store.dispatch(AppAction.leave_room, {'room_id': self.room,
                                              'user_id': self.user})
