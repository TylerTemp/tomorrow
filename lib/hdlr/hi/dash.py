import tornado.web
import logging
try:
    from urllib.parse import unquote, quote
except ImportError:
    from urllib import unquote, quote

import sys
import os
sys.path.insert(0, os.path.normpath(os.path.join(__file__,
                                                 '..', '..', '..', '..')))
from lib.db import User, Article
from lib.hdlr.hi.base import BaseHandler, ItsNotMyself
from lib.tool.md import md2html
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

        intro_info = user_info['intro']
        intro = None
        if intro_info['show_in_home']:
            intro = intro_info['content']
            if intro:
                intro = md2html(intro)

        donate_info = user_info['donate']
        donate = None
        if donate_info['show_in_home']:
            if donate_info['info']:
                donate = donate_info['old']
            else:
                donate = donate_info['new']

            if donate:
                donate = md2html(donate)

        return self.render(
            'hi/home.html',
            user_name=user_name,
            user_img=user_img,
            user_email=user_email,
            user_intro=intro,
            user_donate=donate,
            main_url=main_url,
            article_num=Article.num_by(user_name),
            act='home'
        )
