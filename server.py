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
reserved_usernames = ["anonymous", "", "debug"]

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        if not self.get_secure_cookie("uniqueid"):
            self.set_secure_cookie("uniqueid", hex(randint(0, 1048575))[2:])
        else:
            self.set_secure_cookie("uniqueid", self.get_secure_cookie("uniqueid"))
        self.render("index.html")


class CookieHandler(tornado.web.RequestHandler):
    def post(self):
        username = self.get_argument("username")
        secretkey = self.get_argument("secretkey")
        if user_db[secretkey] == username:
            self.set_secure_cookie("uniqueid", secretkey)


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
                        user_db[client_id] = ""
                    response = {"act": "auth",
                                "username": user_db[client_id],
                                "secretkey": client_id,
                                "response": "success"}
                    print("response: " + str(response))
                    self.write_message(response)

                elif "username" in data:
                    if data["username"] in reserved_usernames:
                        response = {"act": "auth",
                                    "username": user_db[client_id],
                                    "secretkey": client_id,
                                    "response": "fail"}
                    elif data["username"] in user_db.values():
                        if user_db[client_id] == data["username"]:
                            return
                        elif data["secretkey"]:
                            if data["secretkey"] not in user_db:
                                print("secret key not existent")
                                return
                            elif user_db[data["secretkey"]] != data["username"]:
                                print("secret key wrong")
                                return
                            del user_db[client_id]
                            response = {"act": "auth",
                                        "username": user_db[data["secretkey"]],
                                        "secretkey": data["secretkey"],
                                        "response": "changed"}
                        else:
                            response = {"act": "auth",
                                        "username": user_db[client_id],
                                        "secretkey": client_id,
                                        "response": "taken"}
                    else:
                        user_db[client_id] = data["username"]
                        response = {"act": "auth",
                                    "username": user_db[client_id],
                                    "secretkey": client_id,
                                    "response": "success"}
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
         (r"/cookie", CookieHandler),
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
