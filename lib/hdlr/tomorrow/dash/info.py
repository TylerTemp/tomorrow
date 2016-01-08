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
from .base import ItsMyself, BaseHandler

logger = logging.getLogger('tomorrow.dash.info')


class InfoHandler(BaseHandler):
    config = Config()

    @tornado.web.authenticated
    @ItsMyself('info/')
    def get(self, user):

        user = User(self.current_user['user'])
        user_info = user.get()
        size_limit = self.config.size_limit[user_info['type']]
        if size_limit != float('inf'):
            size_limit = '%.2f %s' % unit_satisfy(size_limit)

        return self.render(
            'tomorrow/admin/dash/info.html',
            user_img=user_info.get('img', None),
            user_email=user_info['email'],
            show_email=user_info['show_email'],
            intro=user_info['intro'],
            donate=user_info['donate'],
            size_limit=size_limit,
            active=user_info['active'],
        )

    @tornado.web.authenticated
    @ItsMyself('info/')
    def post(self, user):

        self.check_xsrf_cookie()

        user_info = self.current_user
        url_user = unquote(user)
        if user_info is None or user_info['user'] != url_user:
            raise tornado.web.HTTPError(500, 'user %s try to modify user %s',
                                        user_info['user'], url_user)

        show_email = self.get_bool('show_email')
        show_intro_in_home = self.get_bool('intro_in_home')
        show_intro_in_article = self.get_bool('intro_in_article')
        show_donate_in_home = self.get_bool('donate_in_home')
        show_donate_in_article = self.get_bool('donate_in_article')
        intro_content = self.get_argument('intro', None) or None
        donate_content = self.get_argument('donate', None) or None
        # set to None if it's empty string
        user_img = self.get_argument('img_url', None) or None

        intro = {'content': intro_content,
                 'show_in_home': show_intro_in_home,
                 'show_in_article': show_intro_in_article}
        donate_switch = {'show_in_home': show_donate_in_home,
                  'show_in_article': show_donate_in_article}

        user = User(user_info['user'])
        user_info = user.get()
        user_info.update({'img': user_img, 'show_email': show_email})
        user_info['intro'].update(intro)
        donate = user_info['donate']
        donate.update(donate_switch)

        if donate_content != donate['new']:
            if donate['info'] is None:
                donate['new'], donate['old'] = donate_content, donate['new']
            else:
                donate['new'] = donate_content
            if donate_content:
                donate['info'] = 'pending'
            else:
                donate['info'] = None

        logger.debug('user: %s; show_email: %r; user_img: %r',
                     user_info['user'], show_email, user_img)
        user.save()

        return self.write(json.dumps({'error': 0}))

    def get_bool(self, name, default=False):
        arg = self.get_argument(name, default)
        if arg == 'false':
            arg = False
        return bool(arg)