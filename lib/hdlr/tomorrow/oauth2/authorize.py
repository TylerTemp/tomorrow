import logging
import tornado.web
import tornado.ioloop
from .base import BaseHandler
from lib.db import Auth, User
from lib.tool.generate import generate
import time

try:
    from urllib.parse import urlencode, quote, urlsplit, parse_qs, urlunsplit
except:
    from urlparse import urlencode, quote, urlsplit, parse_qs, urlunsplit

logger = logging.getLogger('tomorrow.oauth.authorize')


class AuthorizeHandler(BaseHandler):

    def get(self):
        self.client_id = self.get_argument('client_id')
        callback = self.get_argument('redirect_uri')
        self.auth = Auth(self.client_id)
        if self.auth.callback != callback:
            raise tornado.web.HTTPError(500, 'Callback unmatch %r' % callback)

        if not self.check_user():
            return

        code = self.set_code()
        self.redirect_to_callback(callback, code)
        self.clear_code(code)

    def check_user(self):
        user = self.current_user
        confirm_url = '/oauth2/confirm/%s/' % quote(self.client_id, '')
        if user is None:
            self.to_login(confirm_url)
            return False

        u = User(user)
        authed = u.authed_app(self.client_id)
        if not authed:
            self.redirect(confirm_url)
            return False

        return True

    def to_login(self, next_uri):
        login_url = self.get_login_url()
        param = {
            'next': next_uri,
        }
        self.redirect('%s?%s' % (login_url, urlencode(param)))

    def set_code(self):
        code = generate()
        auth = self.auth
        auth.set_code(code)
        auth.save()
        return code

    def redirect_to_callback(self, callback, code):
        self.redirect(self.parse_callback(callback, code))

    def clear_code(self, code):
        auth = self.auth
        expire_at = auth.get_expire(code)
        logger.debug('clear at %s', expire_at)
        tornado.ioloop.IOLoop.instance().add_timeout(
            expire_at,
            self.auth.clear_code,
            code
        )
