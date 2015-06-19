#!/usr/bin/python
"""The main entry point for the Web500 program.
"""

import json
import os.path
import sqlite3
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
        print(msg)
        try:
            client_id = self.get_secure_cookie("uniqueid")
            assert(client_id)
            data = json.loads(msg)
            action = data["act"]

            if action == "auth":
                if "secretkey" not in data and "username" not in data:
                    if client_id not in user_db:
                        user_db[client_id] = "anonymous"
                    response = {"act": "auth",
                                "username": user_db[client_id],
                                "secretkey": client_id,
                                "response": "success"}
                    print("response: " + str(response))
                    self.write_message(response)

                if "username" in data and not data["secretkey"]:
                    response = {"act": "auth",
                                "username": data["username"],
                                "secretkey": client_id,
                                "response": "success"}
                    user_db[client_id] = data["username"]
                    print("response: " + str(response))
                    self.write_message(response)

            elif action == "chat":
                response = {"act": "chat",
                            "from": user_db[client_id],
                            "message": data["message"]}
                for s in self.sockets_list:
                    s.write_message(json.dumps(response))

            else:
                self.log_exception(ValueError, "Unknown message action: " + msg, "")
                return

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
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        cookie_secret="Cookiezi")
    application.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


def get_db_connection(db_path):
    """Acquire a connection to a populated user database, performing
    initialisation if necessary."""
    db = sqlite3.connect(db_path)
    try:
        db.execute("SELECT * FROM Users")
    except sqlite3.OperationalError:
        db.execute("CREATE TABLE Users (ID int, Name varchar(128))")
    return db

if __name__ == "__main__":
    users_db = sqlite3.connect("users.db")
    user_db = {}
    main()
