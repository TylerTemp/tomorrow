import os
import functools
import tornado.web
from lib.db.tomorrow import User
from lib.hdlr.base import BaseHandler
import tornado.locale
try:
    from urllib.parse import quote, urljoin
except ImportError:
    from urlparse import quote, urljoin

class BaseHandler(BaseHandler):

    def get_current_user(self):
        user = self.get_secure_cookie('user')
        if user is None:
            return None
        return User.by_id(user.decode('utf-8'))

    def logout(self):
        self.clear_cookie('user')

    def get_user_locale(self):
        arg = self.get_argument('lang', None)
        if arg is not None:
            return tornado.locale.get(arg)
        current_user = self.current_user
        if current_user is None:
            return None
        code = current_user.lang
        if code is None:
            return None
        return tornado.locale.get(code)

class EnsureUser(object):
    level2name = {
        User.NORMAL: 'registered user',
        User.ADMIN: 'administrator',
        User.ROOT: 'super user'
    }

    NORMAL = User.NORMAL
    ADMIN = User.ADMIN
    ROOT = User.ROOT

    def __init__(self, level=ROOT, active=True):
        self._level = level
        self._active = active

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(ins, *a, **k):
            user = ins.current_user
            error = []
            if user.type < self._level:
                error.append('%s only' %  self.level2name[self._level])
            if self._active and not user.active:
                error.append('actived user only')
            if error:
                msg = 'Permission denied: %s' % '; '.join(error)
                raise tornado.web.HTTPError(403, msg)
            return func(ins, *a, **k)

        return tornado.web.authenticated(wrapper)