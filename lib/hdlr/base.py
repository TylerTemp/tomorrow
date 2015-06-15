'''The basic handler of all tornado request
provide some convenient methods'''

import tornado.web
import tornado.locale
import logging
import functools
try:
    from urllib.parse import quote
    from urllib.parse import urlsplit
    from urllib.parse import urlunsplit
    from urllib.parse import urljoin
except ImportError:
    from urlparse import quote
    from urlparse import urlsplit
    from urlparse import urlunsplit
    from urlparse import urljoin

import sys
import os

rootdir = os.path.normpath(os.path.join(__file__, '..', '..', '..'))
sys.path.insert(0, rootdir)
from lib.tool.tracemore import get_exc_plus
from lib.db import User
sys.path.pop(0)

logger = logging.getLogger("tomorrow.base")


class BaseHandler(tornado.web.RequestHandler):

    def render(self, template_name, **kwargs):
        # add ssl var
        # override this method pls use `super`
        kwargs['ssl'] = self.is_ssl()

        return super(BaseHandler, self).render(
            template_name,
            **kwargs
        )
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
        return {'user': user, 'email': email, 'type': int(level),
                'active': active}

    def set_user(self, user, email, type, active, lang=None, temp=False):
        if temp:
            kwd = {'expires_days': None}
        else:
            kwd = {}
        self.set_secure_cookie('user', user, **kwd)
        self.set_secure_cookie('email', email, **kwd)
        self.set_secure_cookie('type', str(type), **kwd)
        self.set_secure_cookie('active', 'true' if active else 'false', **kwd)
        if lang is not None:
            self.set_cookie('lang', lang)

    def safe_redirect(self, url):
        '''replace the host of url to request's host'''
        split = urlsplit(url)
        host = self.request.host
        if split.netloc and (split.netloc != host):
            logger.warning('prevent: %s -> %s', split.netloc, host)
            split = list(split)
            split[1] = host
            return urlunsplit(split)
        return url

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
        self.clear_cookie("user")
        self.clear_cookie('type')
        self.clear_cookie('email')
        self.clear_cookie('lang')

    def is_ajax(self):
        return (self.request.headers.get('X-Requested-With', None) ==
                "XMLHttpRequest")

    def is_ssl(self):
        return (self.request.protocol == 'https')

    @property
    def db(self):    # lazy-load
        return self.application.settings['db']

    def get_user_locale(self):
        code = self.get_argument('lang', self.get_cookie('lang', None))
        if code is None:
            return None
        return tornado.locale.get(code)

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
        if status_code == 404:
            return self.render('404.html')
        r = self.request
        logger.debug('%s - %s' % (r.remote_ip, r.host))
        logging.error('%s' % get_exc_plus())
        if self.application.settings['debug']:
            self.write('''
                <html>
                    <head>
                        <title>%s</title>
                    </head>
                    <body>
                        <h1>%s</h1>
                        <pre>%s</pre>
                    </body>
                </html>''' % (status_code, status_code, get_exc_plus()))
            return self.flush()

        else:
            # uncomment this line for py2
            # return self.__class__.write_error(self, status_code, **kwargs)
            # uncomment this line for py3
            return super(BaseHandler, self).write_error(status_code, **kwargs)


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
