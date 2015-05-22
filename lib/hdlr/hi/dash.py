import tornado.web
import logging
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
from lib.db import User
from lib.db import Message
from lib.db import Article
from lib.hdlr.hi.base import BaseHandler
from lib.hdlr.hi.base import ItsNotMyself
sys.path.pop(0)

logger = logging.getLogger('tomorrow.hi.dash')


class DashboardHandler(BaseHandler):

    @ItsNotMyself('')
    def get(self, user):
        main_url = '/hi/' + user

        user_name = unquote(user)
        u = User(user_name)
        user_info = u.get()
        user_img = user_info.get('img', None)
        if user_info['show_email']:
            user_email = user_info['email']
        else:
            user_email = None

        return self.render(
            'hi/home.html',
            user_name=user_name,
            user_img=user_img,
            user_email=user_email,
            main_url=main_url,
            article_num=Article.num_by(user_name),
            act='home'
        )
