import tornado.web
import logging
import functools
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
from lib.hdlr.base import BaseHandler
from lib.db import User
sys.path.pop(0)

logger = logging.getLogger('tomorrow.dash.base')


class ItsMyself(object):

    def __init__(self, to):
        self._to = to

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(ins, user):
            unquoted = unquote(user)
            if (ins.current_user is None or
                    ins.current_user['user'] != unquoted):
                logger.debug('redirect to visit %s - %s', unquoted, self._to)
                return ins.redirect('/'.join(('/hi', unquoted, self._to)))

            return func(ins, user)

        return wrapper

class BaseHandler(BaseHandler):

    def render(self, template_name, **kwargs):
        user_info = self.current_user

        if 'main_url' not in kwargs:
            kwargs['main_url'] = '/am/%s' % quote(user_info['user'])

        kwargs['main_url'] = self.get_non_ssl(kwargs['main_url'])

        kwargs.setdefault('user_name', user_info['user'])
        kwargs.setdefault('user_type', user_info['type'])
        kwargs.setdefault('act', None)

        kwargs['NORMAL'] = User.normal
        kwargs['ADMIN'] = User.admin
        kwargs['ROOT'] = User.root

        return super(BaseHandler, self).render(
            template_name,
            **kwargs
        )
