import tornado.web
import logging
import sys
import os
import functools

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.db import User
sys.path.pop(0)

class EnsureSsl(object):
    def __init__(self, permanent=False):
        self._prem = permanent

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(ins, *a, **k):
            if (ins.request.protocol != 'https'):
                return ins.redirect(
                    'https://%s%s' % (ins.request.host, ins.request.uri))
            return func(ins, *a, **k)

        return wrapper


class EnsureUser(object):
    level2name = {
        User.normal: 'registered user',
        User.admin: 'administrator',
        User.root: 'super user'
    }
    def __init__(self, level=User.normal, active=True):
        self._level = level
        self._active = active

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(ins, *a, **k):
            user_info = ins.current_user
            error = []
            if user_info['type'] < self._level:
                error.append('%s only' %  self.level2name[self._level])
            if self._active and not user_info['active']:
                error.append('actived user only')
            if error:
                ins.clear()
                ins.set_status(403)
                msg = '<p>Permission denied: %s</p>' % '; '.join(error)
                ins.write(msg)
                return ins.finish()
            return func(ins, *a, **k)

        return tornado.web.authenticated(wrapper)
