import logging
import json
try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote

import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.hdlr.base import BaseHandler
from lib.hdlr.base import EnsureUser
from lib.db import Jolla
from lib.db import User
sys.path.pop(0)

logger = logging.getLogger('tomorrow.jolla.task')

class HomeHandler(BaseHandler):

    def get(self):
        if self.current_user is None:
            allow_task = False
            allow_translate = False
            user_name = None
            user_url = None
        else:
            user_info = self.current_user
            allow_task = (user_info['active'] and
                          user_info['type'] >= User.admin)
            allow_translate = user_info['active']
            user_name = user_info['user']
            user_url = '/am/%s/' % quote(user_name)

        return self.render(
            'jolla/home.html',
            allow_task=allow_task,
            allow_translate=allow_translate,
            user_name=user_name,
            user_url=user_url
        )
