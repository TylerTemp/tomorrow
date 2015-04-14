import tornado.web
import logging

import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.hdlr.base import BaseHandler
sys.path.pop(0)


class AddSlashOr404Handler(BaseHandler):

    def get(self):
        uri = self.request.uri
        if not uri.endswith('/'):
            return self.redirect(uri+'/')
        self.clear()
        self.set_status(404)
        return self.render('404.html')
