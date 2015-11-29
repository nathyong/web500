#!/usr/bin/python
"""The main entry point for the Web500 program.
"""

import logging
import sqlite3
import tornado.ioloop
import tornado.web
import tornado.options as options

from tornado.web import FallbackHandler
from tornado.websocket import WebSocketHandler
from tornado.wsgi import WSGIContainer
from flask import Flask, render_template

import web500.config


options.define("port",
               default=8888,
               help="run on the given port",
               type=int)

app = Flask(__name__)
app.settings = web500.config.settings


@app.route('/')
def index():
    """Handles the index page"""
    return render_template("index.html")


class ChatSocketHandler(WebSocketHandler):
    pass


class GameSocketHandler(WebSocketHandler):
    pass


def main():
    """Entry point to the program."""
    options.parse_command_line()
    application = tornado.web.Application(
        [(r"/chat/ws", ChatSocketHandler),
         (r"/game/ws", GameSocketHandler),
         (r".*", FallbackHandler, dict(fallback=WSGIContainer(app)))])
    application.listen(options.options.port)
    logging.getLogger("tornado.general").info("Server is starting on port {}".format(options.options.port))
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    users_db = sqlite3.connect("users.db")
    user_db = {}
    main()
