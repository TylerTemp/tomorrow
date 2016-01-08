import logging
import tornado.web
import tornado.ioloop
from .base import BaseHandler
from lib.db.tomorrow import Auth, User
from lib.tool.generate import generate
import time

try:
    from urllib.parse import urlencode, quote, urlsplit, parse_qs, urlunsplit
except:
    from urlparse import urlencode, quote, urlsplit, parse_qs, urlunsplit

logger = logging.getLogger('tomorrow.oauth.authorize')


class AuthorizeHandler(BaseHandler):

    def get(self):
        self.key = self.get_argument('key')
        callback = self.get_argument('callback')
        self.auth = Auth(self.key)
        if not self.auth:
            raise tornado.web.HTTPError(500, 'Unknown app %s' % self.key)
        if self.auth.callback != callback:
            logger.debug('source: %s != db: %s', callback, self.auth.callback)
            raise tornado.web.HTTPError(500, 'Callback unmatch %r' % callback)

        code = self.set_code()
        if not self.check_user(code):
            return

        self.redirect_to_callback(callback, code)

    def check_user(self, code):
        user = self.current_user
        confirm_url = ('/oauth2/confirm/%s/%s/' %
                       (quote(self.key, ''),
                        quote(code, '')))

        if user is None:
            self.to_login(confirm_url)
            return False

        u = User(user)
        authed = u.authed_app(self.key)
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
        user = self.current_user['user']
        expire_at = auth.set_code(code, self.get_uid(user))
        auth.save()
        self.clear_at(lambda: auth.clear_code(code), expire_at)
        return code

    def redirect_to_callback(self, callback, code):
        self.redirect(self.parse_callback(callback, code))