import tornado.web
import logging
import json
try:
    from urllib.parse import unquote, quote
except ImportError:
    from urllib import unquote, quote

from lib.db.tomorrow import User
from lib.config import Config
from lib.tool.unitsatisfy import unit_satisfy
from .base import BaseHandler

logger = logging.getLogger('tomorrow.dash.info')


class InfoHandler(BaseHandler):
    config = Config()

    @tornado.web.authenticated
    def get(self):

        user = self.current_user

        size_limit = self.config.size_limit[user.type]

        if size_limit != float('inf'):
            size_limit = '%.2f %s' % unit_satisfy(size_limit)

        return self.render(
            'tomorrow/admin/dash/info.html',
            user=user,
            size_limit=size_limit,
        )

    @tornado.web.authenticated
    def post(self):

        self.check_xsrf_cookie()

        show_email = bool(self.get_argument('show_email', False))
        show_intro_in_home = bool(self.get_argument('intro_in_home', False))
        show_intro_in_article = bool(
            self.get_argument('intro_in_article', False))
        show_donate_in_home = bool(self.get_argument('donate_in_home', False))
        show_donate_in_article = bool(
            self.get_argument('donate_in_article', False))
        intro_zh = self.get_argument('intro-zh', '').strip() or None
        intro_en = self.get_argument('intro-en', '').strip() or None
        donate_zh = self.get_argument('donate-zh', '').strip() or None
        donate_en = self.get_argument('donate-en', '').strip() or None
        # set to None if it's empty string
        user_img = self.get_argument('img_url', '').strip() or None

        user = self.current_user

        intro = user.intro
        if intro_zh:
            intro['zh'] = intro_zh
        if intro_en:
            intro['en'] = intro_en
        u = {'show_in_home': show_intro_in_home,
             'show_in_article': show_intro_in_article}
        intro.update(u)

        donate = user.donate
        if donate_zh:
            donate['zh'] = donate_zh
        if donate_en:
            donate['en'] = donate_en
        u = {'show_in_home': show_donate_in_home,
             'show_in_article': show_donate_in_article}
        donate.update(u)

        user.photo = user_img
        user.save()

        return self.write(json.dumps({'error': 0}))
