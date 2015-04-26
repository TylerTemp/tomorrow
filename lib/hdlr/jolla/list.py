import tornado.web
import logging

import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.hdlr.base import BaseHandler
from lib.db import Jolla
sys.path.pop(0)


# todo: pagination
class ListHandler(BaseHandler):

    def get(self):

        return self.render(
            'jolla/list.html',
            articles=Jolla.all()
        )
