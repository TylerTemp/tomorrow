import tornado.web
import logging

import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.hdlr.base import BaseHandler
sys.path.pop(0)

logger = logging.getLogger('tomorrow.edit')


class EditHandler(BaseHandler):

    def get(self):
        return self.render(
            'edit.html',
            content='',
        )

    def post(self):
        pass
