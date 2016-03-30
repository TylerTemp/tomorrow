'''The basic handler of all tornado request
provide some convenient methods'''

import tornado.web
import tornado.locale
import tornado.escape
import logging
import functools
import json
import os
try:
    from urllib.parse import quote, urlsplit, urlunsplit, urljoin
except ImportError:
    from urllib import quote
    from urlparse import urlsplit, urlunsplit, urljoin


from lib.tool.tracemore import get_exc_plus
from lib.config.base import Config
from lib import Log


class BaseHandler(tornado.web.RequestHandler, Log):
    config = Config()
    logger = logging.getLogger()
    error_template = 'error.html'

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
            self.write({'code': -1, 'message': 'Method Not Allowed',
                        'error': -1})
            return

        raise tornado.web.HTTPError(405, 'Method Not Allowed')

    def render(self, template_name, **kwargs):
        kwargs.setdefault('JOLLA_HOST', self.config.jolla_host)
        kwargs.setdefault('TOMORROW_HOST', self.config.tomorrow_host)

        return super(BaseHandler, self).render(
            template_name,
            **kwargs
        )

    def is_ajax(self):
        return (self.request.headers.get('X-Requested-With', None) ==
                "XMLHttpRequest")

    def is_ssl(self):
        return (self.request.protocol == 'https')

    def _list_path(self, path):
        if not os.path.exists(path):
            return []
        for dirpath, dirnames, filenames in os.walk(path):
            return list(filenames)

    def get_user_locale(self):
        arg = self.get_argument('lang', None)
        if arg is not None:
            return tornado.locale.get(arg)
        cookie_lang = self.get_cookie('lang')
        if cookie_lang:
            return tornado.locale.get(cookie_lang)
        return None

    def write_error(self, status_code, **kwargs):
        r = self.request
        self.debug('%s - %s' % (r.remote_ip, r.host))
        self.error('%s' % get_exc_plus())

        self.clear()
        self.set_status(status_code)
        message = self.get_error(status_code, **kwargs)

        if self.is_ajax():
            self.debug('render error of ajax')
            self.write({'code': -1, 'message': message, 'error': -1})
            return

        self.debug('render error of html')
        return self.render(
            self.error_template,
            code=status_code,
            msg=message,
        )

    def get_error(self, status_code, **kwargs):
        msg = 'Unknown Error'

        if self.settings['debug']:
            if self.is_ajax():
                exc_info = kwargs['exc_info']
                return (getattr(exc_info[1], 'log_message', None) or
                        str(exc_info[1]))

            return get_exc_plus()

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


class RedirectHandler(BaseHandler):

    def initialize(self, to, permanently=False):
        self._to = to
        self._permanently = permanently

    def get(self, *a, **k):
        return self.redirect(self._to, self._permanently)

    post = get
