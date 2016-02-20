import logging
from .base import BaseHandler


class LogoutHandler(BaseHandler):
    logger = logging.getLogger('tomorrow.auth.logout')

    def get(self):
        self.logout()
        return self.redirect('/')

    post = get
