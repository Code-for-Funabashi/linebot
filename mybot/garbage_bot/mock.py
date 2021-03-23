
# TODO: Build a mock server.
from unittest import mock

import tornado.ioloop
import tornado.web
import logging



class LineMock(tornado.web.RequestHandler):
    def get(self):
        print("hoge")
        self.write("Hello, world")

def make_app():
    return tornado.web.Application([
        (r"/", LineMock),
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
