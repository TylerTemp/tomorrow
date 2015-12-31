import tornado.web
import logging
import functools
try:
    from urllib.parse import unquote, quote
except ImportError:
    from urllib import unquote, quote

from lib.hdlr.base import BaseHandler
from lib.db import User

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
                ins.user_name = user
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

        if 'user_name' not in kwargs:
            kwargs['user_name'] = getattr(self, 'user_name', '-')

        return super(BaseHandler, self).render(
            template_name,
            **kwargs
        )

    def write_error(self, status_code, **kwargs):
        msg = self.get_error(status_code, **kwargs)

        return self.render(
            'tomorrow/admin/hi/error.html',
            code=status_code,
            msg=msg
        )