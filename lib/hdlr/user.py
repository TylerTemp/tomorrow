import tornado.web
import logging
import json
try:
    from urllib.parse import unquote
except ImportError:
    from urllib import unquote

import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.hdlr.base import BaseHandler
from lib.db import User
sys.path.pop(0)

logger = logging.getLogger('tomorrow.user')

class UserHandler(BaseHandler):


    def get(self, user):

        user = unquote(user)

        userinfo = self.get_current_user()

        if user.lower() != userinfo['user'].lower():
            # show person's information
            return self.show_info(user)

        return self.render(
            'hi.html',
            user=userinfo['user']
        )
    def show_info(self, user):
        assert False
