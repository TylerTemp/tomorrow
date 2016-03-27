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
from lib.config.tomorrow import Config


class BaseHandler(BaseHandler):
    config = Config()

    def render(self, template_name, **kwargs):
        kwargs.setdefault('HOST', self.config.host)

        return super(BaseHandler, self).render(
            template_name,
            **kwargs
        )


    def get_user_path(self, user):
        return os.path.join(self.config.root, 'static', 'tomorrow', user)

    def get_current_user(self):
        user = self.get_secure_cookie('user')
        if user is None:
            return None
        return User.by_id(user.decode('utf-8'))

    def login(self, user, temp=False):
        if temp:
            kwd = {'expires_days': None}
        else:
            kwd = {}
        self.set_secure_cookie('user', str(user._id), **kwd)

    def logout(self):
        self.clear_cookie('user')


class EnsureUser(object):
    level2name = {
        User.NORMAL: 'registered user',
        User.ROOT: 'super user'
    }

    NORMAL = User.NORMAL
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
