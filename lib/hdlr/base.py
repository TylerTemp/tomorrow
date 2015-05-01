'''The basic handler of all tornado request
provide some convenient methods'''

import tornado.web
import logging
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

    def get_current_user(self):
        user = self.get_secure_cookie("user")

        if user is None:
            return None

        user = user.decode('utf-8')
        email = self.get_secure_cookie('email').decode('utf-8')
        level = self.get_secure_cookie('type')

        return {'user': user, 'email': email, 'type': int(level)}

    def set_user(self, user, email, type, temp=False):
        if temp:
            kwd = {'expires_days': None}
        else:
            kwd = {}
        self.set_secure_cookie('user', user, **kwd)
        self.set_secure_cookie('email', email, **kwd)
        self.set_secure_cookie('type', str(type), **kwd)

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

    def get_user_path(self, user):
        return os.path.join(rootdir, 'static', 'upload', user)

    def get_user_url(self, user):
        return '/static/upload/%s/' % quote(user)

    def logout(self):
        self.clear_cookie("user")
        self.clear_cookie('type')
        self.clear_cookie('email')


    def is_ajax(self):
        return (self.request.headers.get('X-Requested-With', None) ==
                "XMLHttpRequest")

    @property
    def db(self):    # lazy-load
        return self.application.settings['db']

    # def get_user_locale(self):
        # todo: able to change
        # return tornado.locale.get('zh_CN')

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
            logging.error('%s' % get_exc_plus())
            # uncomment this line for py2
            # return self.__class__.write_error(self, status_code, **kwargs)
            # uncomment this line for py3
            return super(BaseHandler, self).write_error(status_code, **kwargs)
