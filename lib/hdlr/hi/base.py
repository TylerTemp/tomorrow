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

logger = logging.getLogger('tomorrow.hi.base')


class ItsNotMyself(object):

    def __init__(self, to):
        self._to = to

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(ins, user):
            unquoted = unquote(user)
            u = User(unquoted)
            if u.new:
                raise tornado.web.HTTPError(404, 'User %s not found' % unquoted)
            if (ins.current_user is not None and
                    ins.current_user['user'] == unquoted):
                logger.debug('redirect to dashboard %s - %s',
                             unquoted, self._to)
                return ins.redirect('/'.join(('/am', unquoted, self._to)))

            return func(ins, user)

        return wrapper


class BaseHandler(BaseHandler):

    def render(self, template_name, **kwargs):
        if 'visitor' not in kwargs:
            kwargs['visitor'] = self.current_user and self.current_user['user']

        return super(BaseHandler, self).render(
            template_name,
            **kwargs
        )
