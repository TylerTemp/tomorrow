import logging
from .base import BaseHandler


class ForgetHandler(BaseHandler):
    logger = logging.getLogger('tomorrow.auth.forget')

    def get(self):
        return self.render(
            'tomorrow/blog/auth/forget.html',
            user=self.get_argument('user', None),
        )
