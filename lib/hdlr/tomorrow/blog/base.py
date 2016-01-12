import logging
from lib.hdlr.tomorrow.base import BaseHandler

logger = logging.getLogger('tomorrow.blog')


class BaseHandler(BaseHandler):

    def render(self, template_name, **kwargs):
        if 'user' not in kwargs:
            kwargs['user'] = self.current_user

        return super(BaseHandler, self).render(template_name, **kwargs)

    def write_error(self, status_code, **kwargs):
        msg = self.get_error(status_code, **kwargs)

        return self.render(
            'tomorrow/blog/error.html',
            code=status_code,
            msg=msg
        )