import tornado.web
import sys
import os

blacklist = open('/tmp/blacklist', 'a')

class BlackListHandler(tornado.web.RequestHandler):

    def get(self):
        blacklist.write(self.request.remote_ip)
        blacklist.flush()

    post = get
