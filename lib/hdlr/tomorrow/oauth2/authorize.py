import logging
import tornado.web
from .base import BaseHandler
from lib.db import Auth, User

try:
    from urllib.parse import urlencode
except:
    from urlparse import urlencode

logger = logging.getLogger('tomorrow.oauth.authorize')


class AuthorizeHandler(BaseHandler):

    def get(self):
        self.client_id = self.get_argument('client_id')
        callback = self.get_argument('redirect_uri')
        auth = Auth(self.client_id)
        if auth.callback != callback:
            raise tornado.web.HTTPError(500, 'Callback unmatch %r' % callback)

        user = self.get_user()
        if user is None:
            return

    def get_user(self):
        user = self.current_user
        if user is None:
            login_url = self.get_login_url()
            param = {'next': self.request.uri}
            self.redirect('%s?%s' % (login_url, urlencode(param)))
            return