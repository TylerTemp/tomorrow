'''The basic handler of all tornado request
provide some convenient methods'''

import tornado.web
import tornado.locale
import tornado.escape
import logging
import functools
import json
try:
    from urllib.parse import quote, urlsplit, urlunsplit, urljoin
except ImportError:
    from urllib import quote
    from urlparse import urlsplit, urlunsplit, urljoin

import sys
import os

rootdir = os.path.normpath(os.path.join(__file__, '..', '..', '..'))
sys.path.insert(0, rootdir)
from lib.tool.tracemore import get_exc_plus
from lib.db import User
from lib.config import Config
sys.path.pop(0)

logger = logging.getLogger("tomorrow.base")


class BaseHandler(tornado.web.RequestHandler):
    cfg = Config()

    def get(self, *a, **k):
        splited = urlsplit(self.request.uri)
        if not splited.path.endswith('/'):
            to_list = list(splited)
            to_list[2] = splited.path + '/'
            return self.redirect(urlunsplit(to_list), True)
        raise tornado.web.HTTPError(404)

    def post(self, *a, **k):
        if self.is_ajax():
            self.clear()
            self.set_status(405)
            self.write(json.dumps({'code': -1, 'message': 'Method Not Allowed',
                                   'error': -1}))
            return

        raise tornado.web.HTTPError(405, 'Method Not Allowed')

    def render(self, template_name, **kwargs):
        kwargs['ssl'] = self.is_ssl()
        kwargs.setdefault('nav_active', None)

        if self.current_user is None:
            kwargs.setdefault('user_name', None)
            kwargs.setdefault('user_link', None)

        if 'user_name' not in kwargs:
            kwargs['user_name'] = self.current_user['user']

        if 'user_link' not in kwargs:
            kwargs['user_link'] = '/am/%s/' % quote(kwargs['user_name'])

        kwargs.setdefault('JOLLA_HOST', self.cfg.jolla_host)
        kwargs.setdefault('MAIN_HOST', self.cfg.main_host)

        assert 'static_path' not in kwargs
        kwargs['static_path'] = self.static_path

        return super(BaseHandler, self).render(
            template_name,
            **kwargs
        )

    def static_path(self, url):
        return '//%s/static/%s' % (self.cfg.main_host, quote(url))

    def get_current_user(self):
        user = self.get_secure_cookie("user")

        if user is None:
            return None

        user = user.decode('utf-8')
        email = self.get_secure_cookie('email').decode('utf-8')
        level = self.get_secure_cookie('type')
        active = (True
                  if self.get_secure_cookie('active').decode('utf-8') == 'true'
                  else False)
        service = self.get_secure_cookie('service')
        return {'user': user, 'email': email, 'type': int(level),
                'active': active,
                'service':
                    service.decode('utf-8').split('|') if service else ()}

    def set_user(self, user, email, type, active, service=None,
                 lang=None, temp=False):
        if temp:
            kwd = {'expires_days': None}
        else:
            kwd = {}
        self.set_secure_cookie('user', user, **kwd)
        self.set_secure_cookie('email', email, **kwd)
        self.set_secure_cookie('type', str(type), **kwd)
        self.set_secure_cookie('active', 'true' if active else 'false', **kwd)
        if service:
            self.set_secure_cookie('service', '|'.join(service))
        if lang is not None:
            self.set_cookie('lang', lang)

    def get_ssl(self, uri=None):
        uri = uri or self.request.uri
        splited = urlsplit(uri)
        to_list = list(splited)
        if not splited.netloc:
            to_list[1] = self.request.host
        to_list[0] = 'https'
        return urlunsplit(to_list)

    def get_non_ssl(self, uri=None):
        uri = uri or self.request.uri
        splited = urlsplit(uri)
        to_list = list(splited)
        if not splited.netloc:
            to_list[1] = self.request.host
        to_list[0] = 'http'
        return urlunsplit(to_list)

    def get_user_path(self, user):
        return os.path.join(rootdir, 'static', 'upload', user)

    def get_user_url(self, user):
        return '/static/upload/%s/' % quote(user)

    def logout(self):
        self.clear_cookie('user')
        self.clear_cookie('type')
        self.clear_cookie('email')
        self.clear_cookie('service')

    def is_ajax(self):
        return (self.request.headers.get('X-Requested-With', None) ==
                "XMLHttpRequest")

    def is_ssl(self):
        return (self.request.protocol == 'https')

    def get_user_locale(self):
        code = self.get_argument('lang', self.get_cookie('lang', None))
        if code is None:
            return None
        return tornado.locale.get(code)

    def get_bool(self, name, default=False):
        arg = self.get_argument(name, default)
        if arg == 'false':
            return False
        return bool(arg)

    def get_imgs_and_files(self, user, type):
        allow_update = (type >= User.admin)
        if not allow_update:
            return None, None
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

    def _list_path(self, path):
        if not os.path.exists(path):
            return []
        for dirpath, dirnames, filenames in os.walk(path):
            return list(filenames)

    def write_error(self, status_code, **kwargs):
        r = self.request
        logger.debug('%s - %s' % (r.remote_ip, r.host))
        logging.error('%s' % get_exc_plus())

        if self.is_ajax():
            self.clear()
            self.set_status(status_code)
            self.write(
                json.dumps({'code': -1, 'message': 'Unknown Error',
                            'error': -1}))
            return

        msg = self.get_error(status_code, **kwargs)
        return self.render(
            'error.html',
            code=status_code,
            msg=msg,
        )

    def get_error(self, status_code, **kwargs):
        msg = None

        if self.settings['debug']:
            if self.is_ajax():
                exc_info = kwargs['exc_info']
                return (getattr(exc_info[1], 'log_message', None) or
                        str(exc_info[1]))

            msg = ('<pre><code>%s</code></pre>' %
                   tornado.escape.xhtml_escape(get_exc_plus()))

        elif status_code == 404:
            msg = 'Page Not Found'
            if 'exc_info' in kwargs:
                exc_info = kwargs['exc_info']
                if exc_info and len(exc_info) >= 2:
                    msg = getattr(exc_info[1], 'log_message', None) or msg

        return msg


class EnsureSsl(object):

    def __init__(self, permanent=False):
        self._prem = permanent

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(ins, *a, **k):
            if (ins.request.protocol != 'https'):
                return ins.redirect(
                    'https://%s%s' % (ins.request.host, ins.request.uri),
                    self._prem)
            return func(ins, *a, **k)

        return wrapper


class StaticFileHandler(tornado.web.StaticFileHandler):

    def get(self):
        path, file = os.path.split(self.root)
        self.root = path
        return super(StaticFileHandler, self).get(path=file)


class EnsureUser(object):
    level2name = {
        User.normal: 'registered user',
        User.admin: 'administrator',
        User.root: 'super user'
    }

    NORMAL = User.normal
    ADMIN = User.admin
    ROOT = User.root

    def __init__(self, level=ROOT, active=True):
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
                msg = 'Permission denied: %s' % '; '.join(error)
                raise tornado.web.HTTPError(403, msg)
            return func(ins, *a, **k)

        return tornado.web.authenticated(wrapper)
