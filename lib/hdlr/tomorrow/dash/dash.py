import tornado.web
import logging
import os
try:
    from urllib.parse import unquote, quote
except ImportError:
    from urllib import unquote, quote

from lib.db.tomorrow import User, Article
from .base import BaseHandler


class DashboardHandler(BaseHandler):
    logger = logging.getLogger('tomorrow.dash.home')

    @tornado.web.authenticated
    def get(self):

        user = self.current_user

        return self.render(
            'tomorrow/dash/home.html',
            user=user,
        )
