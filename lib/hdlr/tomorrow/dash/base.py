import tornado.web
import logging
try:
    from urllib.parse import unquote
    from urllib.parse import quote
except ImportError:
    from urllib import unquote
    from urllib import quote

from lib.hdlr.tomorrow.base import BaseHandler


class BaseHandler(BaseHandler):
    logger = logging.getLogger('tomorrow.dash')

    def render(self, template_name, **kwargs):
        if 'user' not in kwargs:
            kwargs['user'] = self.current_user
        kwargs.setdefault('user', self.current_user)
        kwargs.setdefault('MESSAGENUM', 0)
        kwargs.setdefault('SERVICE', None)

        return super(BaseHandler, self).render(
            template_name,
            **kwargs
        )

    def write_error(self, status_code, **kwargs):
        msg = self.get_error(status_code, **kwargs)

        return self.render(
            'tomorrow/dash/error.html',
            code=status_code,
            msg=msg
        )