import tornado.web
import logging
import json
try:
    from urllib.parse import unquote
    from urllib.parse import quote
except ImportError:
    from urllib import unquote
    from urllib import quote

import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.hdlr.base import BaseHandler, EnsureUser
from lib.db import Article, User
sys.path.pop(0)

logger = logging.getLogger('tomorrow.edit')


class EditHandler(BaseHandler):

    @EnsureUser(level=User.root, active=True)
    def get(self, slug=None):
        user_info = self.current_user
        user_name = user_info['user']
        user_slug = quote(user_name)
        return self.render(
            'edit.html',
            img_upload_url='/am/%s/img/' % user_slug,
            file_upload_url='/am/%s/file/' % user_slug
        )
