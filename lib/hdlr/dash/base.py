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
from lib.hdlr.base import BaseHandler
from lib.db import User
sys.path.pop(0)

logger = logging.getLogger('tomorrow.dash.base')


def its_myself(func):

    def wrapper(self, user):
        user_info = self.current_user
        url_user = unquote(user)
        if user_info is None or user_info['user'] != url_user:
            logger.debug('redirect to visit %s', url_user)
            return self.redirect('/hi/%s/' % user)

        return func(self, user)

    return wrapper


class BaseHandler(BaseHandler):

    def render(self, template_name, **kwargs):
        user_info = self.current_user

        if 'main_url' not in kwargs:
            kwargs['main_url'] = '/am/%s' % quote(user_info['user'])

        kwargs['main_url'] = self.get_non_ssl(kwargs['main_url'])

        if 'user_name' not in kwargs:
            kwargs['user_name'] = user_info['user']
        if 'user_type' not in kwargs:
            kwargs['user_type'] = user_info['type']

        kwargs['NORMAL'] = User.normal
        kwargs['ADMIN'] = User.admin
        kwargs['ROOT'] = User.root

        return super(BaseHandler, self).render(
            template_name,
            **kwargs
        )
