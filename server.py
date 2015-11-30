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
from web500.db import get_db, query_db

options.define("port",
               default=8888,
               help="run on the given port",
               type=int)


class GameSocketHandler(WebSocketHandler):
    pass


def main():
    """Entry point to the program."""
    options.parse_command_line()
    application = tornado.web.Application(
        [(r"/chat/ws", web500.ChatSocketHandler),
         (r"/game/ws", GameSocketHandler),
         (r".*", FallbackHandler, dict(fallback=WSGIContainer(web500.app)))])
    application.listen(options.options.port)
    logger = logging.getLogger("tornado.general")
    with web500.app.app_context():
        db = get_db()
        if not query_db("""SELECT * FROM sqlite_master
                        WHERE name ='users' and type='table';"""):
            logger.info("Initialising database")
            with web500.app.open_resource('schema.sql', mode='r') as f:
                db.cursor().executescript(f.read())
            db.commit()
    logger.info("Server is starting on port {}".format(options.options.port))
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
