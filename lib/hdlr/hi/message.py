import tornado.web
import logging
import bleach
import re
import json
try:
    from urllib.parse import unquote
except ImportError:
    from urllib import unquote

import sys
import os
sys.path.insert(0, os.path.normpath(os.path.join(__file__,
                                                 '..', '..', '..', '..')))
from lib.db import Message
from lib.hdlr.hi.base import BaseHandler
from lib.hdlr.hi.base import ItsNotMyself
sys.path.pop(0)

logger = logging.getLogger('tomorrow.hi.message')


class MessageHandler(BaseHandler):
    EMAIL_RE = re.compile(r'^[\w\d.+-]+@([\w\d.]+\.)+\w{2,}$')
    ERROR_CONTENT_EMPTY = 1
    ERROR_WRONG_FORMAT = 2

    @ItsNotMyself('message/')
    def get(self, user):
        user_name = unquote(user)
        main_url = '/hi/' + user

        return self.render(
            'hi/message.html',
            main_url=main_url,
            user_name=user_name,
            act='msg'
        )

    @ItsNotMyself('message/')
    def post(self, user):
        self.check_xsrf_cookie()

        to = unquote(user)
        from_ = ((self.current_user and self.current_user['user']) or
                 self.get_argument('user'))

        # normally this will be redirect to "/am/<user>/message/"
        if ((from_ == to) or
                (self.current_user and self.current_user['email'] == to)):
            raise web.tornado.HTTPError(
                500, '%s want to send to self %s' % (from_, to))

        flag = 0

        content = self.get_argument('msg')
        logger.info('send msg(%s...) from %s to %s', content[:10], from_, to)
        if not content:
            logger.debug('content empty')
            flag |= self.ERROR_CONTENT_EMPTY

        if self.current_user is None and self.EMAIL_RE.match(from_) is None:
            logger.debug('email invalid')
            flag |= self.ERROR_WRONG_FORMAT

        if flag == 0:
            Message().send(from_, to, content)

        return self.write(json.dumps({'error': flag, 'from': from_, 'to': to}))
