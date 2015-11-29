#!/usr/bin/python
"""The main entry point for the Web500 program.
"""

import logging
import tornado.ioloop
import tornado.web
import tornado.options as options
from tornado.web import FallbackHandler
from tornado.websocket import WebSocketHandler
from tornado.wsgi import WSGIContainer

import web500

options.define("port",
               default=8888,
               help="run on the given port",
               type=int)

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
         (r".*", FallbackHandler, dict(fallback=WSGIContainer(web500.app)))])
    application.listen(options.options.port)
    logging.getLogger("tornado.general").info("Server is starting on port {}".format(options.options.port))
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    user_db = {}
    main()
