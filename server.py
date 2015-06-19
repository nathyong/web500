#!/usr/bin/python

import json
import os.path
import tornado.ioloop
import tornado.web
import tornado.websocket

from random import randint
from tornado.options import define, options, parse_command_line

import lib500

define("port", default=8888, help="run on the given port", type=int)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


class SocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print("WebSocket opened")

    def on_message(self, data):
        msg = json.loads(data)
        self.write_message(data)

    def on_close(self):
        print("WebSocket closed")


class GameInstance(object):
    pass


gameInstanceTracker = {}


def main():
    parse_command_line()
    application = tornado.web.Application(
        [(r"/", MainHandler),
         (r"/socket", SocketHandler)],
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        template_path=os.path.join(os.path.dirname(__file__), "templates"))
    application.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
