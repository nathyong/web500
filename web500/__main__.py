#!/usr/bin/python
"""The main entry point for the Web500 program.
"""

import tornado.ioloop
import tornado.web
import tornado.options as options
from tornado.web import FallbackHandler
from tornado.wsgi import WSGIContainer

import web500

options.define("port",
               default=8888,
               help="run on the given port",
               type=int)


def main():
    """Entry point to the program."""
    options.parse_command_line()

    application = tornado.web.Application(
        [(r"/room/([a-z0-9]+)/ws", web500.GameSocketHandler),
         (r".*", FallbackHandler, dict(fallback=WSGIContainer(web500.app)))])
    application.listen(options.options.port)

    web500.app.logger.info("Server is starting on port {}"
                           .format(options.options.port))

    web500.store._logger = web500.app.logger
    web500.store.dispatch(web500.actions.AppAction.init, {})
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
