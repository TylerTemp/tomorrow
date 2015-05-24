import tornado.web
import logging
import json
from bson.objectid import ObjectId
try:
    from urllib.parse import unquote
    from urllib.parse import quote
except ImportError:
    from urllib import unquote
    from urllib import quote

import sys
import os
sys.path.insert(0, os.path.normpath(os.path.join(__file__,
                                                 '..', '..', '..', '..')))
from lib.hdlr.dash.base import BaseHandler
sys.path.pop(0)


class JollaHandler(BaseHandler):

    def get(self, user):

        return self.render(
            'dash/manage/jolla.html',
            act='jolla'
        )
