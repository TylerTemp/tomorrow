import os
import functools
import tornado.web
from lib.db.tomorrow import User
from lib.hdlr.base import BaseHandler
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

    def get_imgs_and_files(self, user):
        path = self.get_user_path(user)
        link = self.get_user_url(user)
        imgs = self._list_path(os.path.join(path, 'img'))
        files = self._list_path(os.path.join(path, 'file'))
        img_name_and_link = {
            name: urljoin(link, 'img/%s' % quote(name))
            for name in imgs}

        file_name_and_link = {
            name: urljoin(link, 'file/%s' % quote(name))
            for name in files}

        return img_name_and_link, file_name_and_link


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