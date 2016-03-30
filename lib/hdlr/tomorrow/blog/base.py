import logging
from lib.hdlr.tomorrow.base import BaseHandler


class BaseHandler(BaseHandler):
    logger = logging.getLogger('tomorrow.blog')
    error_template = 'tomorrow/blog/error.html'

    def render(self, template_name, **kwargs):
        if 'user' not in kwargs:
            kwargs['user'] = self.current_user

        return super(BaseHandler, self).render(template_name, **kwargs)
