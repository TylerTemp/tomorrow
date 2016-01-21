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

logger = logging.getLogger("tomorrow.base")


class BaseHandler(tornado.web.RequestHandler):
    config = Config()

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
        kwargs.setdefault('JOLLA_HOST', self.config.jolla_host)
        kwargs.setdefault('TOMORROW_HOST', self.config.tomorrow_host)

        # assert 'static_path' not in kwargs, kwargs['static_path']
        kwargs['static_path'] = self.static_path

        return super(BaseHandler, self).render(
            template_name,
            **kwargs
        )

    def static_path(self, url):
        return '//%s/static/%s' % (self.config.tomorrow_host, quote(url))

    def get_user_path(self, user):
        return os.path.join(self.config.root, 'static', 'upload', user)

    def get_user_url(self, user):
        return '/static/upload/%s/' % quote(user)

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
