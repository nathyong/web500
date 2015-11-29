#!/usr/bin/python
"""The main entry point for the Web500 program.
"""


import json
import tornado.ioloop
import tornado.web
import tornado.websocket


class SocketHandler(tornado.websocket.WebSocketHandler):
    """Websocket handler for the program.  Contains most of the application
    logic since websockets are the primary form of communication with the
    client.
    """
    sockets_list = []
    user_db = None

    def __init__(self, user_db):
        tornado.websocket.WebSocketHandler.__init__(self)
        self.user_db = user_db

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
                    if client_id not in self.user_db:
                        self.user_db[client_id] = ""
                    response = {"act": "auth",
                                "username": self.user_db[client_id],
                                "secretkey": client_id,
                                "response": "success"}
                    print("response: " + str(response))
                    self.write_message(response)

                elif "username" in data:
                    if data["username"] in reserved_usernames:
                        response = {"act": "auth",
                                    "username": self.user_db[client_id],
                                    "secretkey": client_id,
                                    "response": "fail"}
                    elif data["username"] in self.user_db.values():
                        if self.user_db[client_id] == data["username"]:
                            return
                        elif data["secretkey"]:
                            if data["secretkey"] not in self.user_db:
                                return
                            elif self.user_db[data["secretkey"]] != data["username"]:
                                return
                            del self.user_db[client_id]
                            response = {"act": "auth",
                                        "username": self.user_db[data["secretkey"]],
                                        "secretkey": data["secretkey"],
                                        "response": "changed"}
                        else:
                            response = {"act": "auth",
                                        "username": self.user_db[client_id],
                                        "secretkey": client_id,
                                        "response": "taken"}
                    else:
                        self.user_db[client_id] = data["username"]
                        response = {"act": "auth",
                                    "username": self.user_db[client_id],
                                    "secretkey": client_id,
                                    "response": "success"}
                    print("response: " + str(response))
                    self.write_message(response)

                debug_response = {"act": "chat",
                                  "from": "debug",
                                  "message": str(response)}
                self.write_message(json.dumps(debug_response))

            elif action == "chat":
                response = {"act": "chat",
                            "from": self.user_db[client_id],
                            "message": data["message"]}
                for s in self.sockets_list:
                    s.write_message(json.dumps(response))

            else:
                self.log_exception(ValueError, "Unknown message action: " + msg, "")
                return

        except ValueError:
            self.log_exception(ValueError, "Badly formatted message: " + msg, "")
            return

    def on_connection_close(self):
        self.sockets_list.remove(self)


