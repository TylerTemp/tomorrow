import tornado.web
import logging
import functools
try:
    from urllib.parse import unquote
    from urllib.parse import quote
except ImportError:
    from urllib import unquote
    from urllib import quote

from lib.hdlr.base import BaseHandler
from lib.db import User, Message

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

        if 'MESSAGENUM' not in kwargs:
            name = user_info['user']
            num = Message.num_to(name)
            kwargs['MESSAGENUM'] = num

        if 'SERVICE' not in kwargs:
            kwargs['SERVICE'] = user_info['service']

        # kwargs['main_url'] = self.get_non_ssl(kwargs['main_url'])

        kwargs.setdefault('user_name', user_info['user'])
        kwargs.setdefault('user_type', user_info['type'])

        kwargs['NORMAL'] = User.normal
        kwargs['ADMIN'] = User.admin
        kwargs['ROOT'] = User.root

        return super(BaseHandler, self).render(
            template_name,
            **kwargs
        )

    def write_error(self, status_code, **kwargs):
        msg = self.get_error(status_code, **kwargs)

        return self.render(
            'tomorrow/admin/dash/error.html',
            code=status_code,
            msg=msg
        )