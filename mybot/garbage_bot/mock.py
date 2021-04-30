# TODO: Build a mock server.
from unittest import mock
import tornado.ioloop
import tornado.web
import logging
import requests
from secrets import token_hex
import os
import json
from requests.exceptions import ConnectionError


LINE_ACCESS_TOKEN = os.environ["LINE_ACCESS_TOKEN"]

class LineMock(tornado.web.RequestHandler):
    def get(self):
        print("hoge")
        self.write("Hello, world")

    def post(self):
        print("post(line user sent a message)")
        text = "燃えるゴミの日いつ？"
        reply_token = token_hex(16)
        body = {
        # "replyToken":reply_token,
            "events":{
                "replyToken":reply_token,
                "message":[
                    {
                        "type":"text",
                        "text":f"Hello, user\n {text}"
                    },
                ]
            }
        }

        # dispatch
        try:
            requests.post("http://localhost:8080/callback", 
                    headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {LINE_ACCESS_TOKEN}'},
                    data=json.dumps(body)
                )
        except ConnectionError as ce:
            print("Something wrong in the banckend server...\n With the following error-----\n")
            print(ce)

def make_app():
    return tornado.web.Application([
        (r"/", LineMock),
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
