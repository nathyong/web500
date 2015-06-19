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
reserved_usernames = ["anonymous"]


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        if not self.get_secure_cookie("uniqueid"):
            self.set_secure_cookie("uniqueid", hex(randint(0, 1048575))[2:])
        else:
            self.set_secure_cookie("uniqueid", self.get_secure_cookie("uniqueid"))
        self.render("index.html")


class SocketHandler(tornado.websocket.WebSocketHandler):
    sockets_list = []

    def open(self):
        self.sockets_list.append(self)

    def on_message(self, msg):
        try:
            data = json.loads(msg)
            action = data["act"]

            if action == "auth":
                pass
            elif action == "chat":
                response = {"message": data["message"]}
            else:
                self.log_exception(KeyError, "Unknown message action: " + msg, "")
                return

            for s in self.sockets_list:
                s.write_message(json.dumps(response))

        except ValueError:
            self.log_exception(ValueError, "Badly formatted message: " + msg, "")
            return
        except KeyError:
            self.log_exception(KeyError, "Message received without action: " + msg, "")
            return

    def on_connection_close(self):
        self.sockets_list.remove(self)


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
