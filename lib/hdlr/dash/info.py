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
sys.path.insert(0, os.path.normpath(os.path.join(__file__,
                                                 '..', '..', '..', '..')))
from lib.db import User
from lib.config import Config
from lib.hdlr.dash.base import ItsMyself
from lib.hdlr.dash.base import BaseHandler
from lib.tool.unitsatisfy import unit_satisfy
sys.path.pop(0)

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
            'dash/info.html',
            user_img=user_info.get('img', None),
            user_email=user_info['email'],
            show_email=user_info['show_email'],
            size_limit=size_limit,
            act=('info', ),
        )

    @tornado.web.authenticated
    @ItsMyself('info/')
    def post(self, user):

        self.check_xsrf_cookie()

        user_info = self.current_user
        url_user = unquote(user)
        if user_info is None or user_info['user'] != url_user:
            raise tornado.web.HTTPError(500, 'user %s try to modefy user %s',
                                        user_info['user'], url_user)

        # this should be bool. But I get string('true'/'false'). WHY?
        show_email = self.get_argument('show_email')
        # set to None if it's empty string
        user_img = self.get_argument('img_url', None) or None
        if show_email not in (True, False):
            logger.info('get show_email (%r) of type (%s)',
                        show_email, type(show_email))
            show_email = {'true': True, 'false': False}[show_email]
        user = User(user_info['user'])
        user_info = user.get()
        user_info.update({'img': user_img, 'show_email': show_email})
        logger.debug('user: %s; show_email: %r; user_img: %r',
                     user_info['user'], show_email, user_img)
        user.save()

        return self.write(json.dumps({'error': 0}))
