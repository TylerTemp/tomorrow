
'''The basic handler of all tornado request
provide some convenient methods'''
import tornado.web
import logging
try:
    from urllib.parse import quote
    from urllib.parse import urlsplit
    from urllib.parse import urlunsplit
except ImportError:
    from urlparse import quote
    from urlparse import urlsplit
    from urlparse import urlunsplit

import sys
import os

rootdir = os.path.normpath(os.path.join(__file__, '..', '..', '..'))
sys.path.insert(0, rootdir)
from lib.tool.tracemore import get_exc_plus
sys.path.pop(0)

logger = logging.getLogger("tomorrow.base")


class BaseHandler(tornado.web.RequestHandler):

    def get_current_user(self):
        user = self.get_cookie("user")
        verify = self.get_secure_cookie("verify")
        level = self.get_secure_cookie('type')
        if verify is None:
            return None
        verify = verify.decode('utf-8')[::-1]
        if user != verify:
            return None
        return {'user': user, 'type': int(level)}

    def set_user(self, user, type, temp=False):
        if temp:
            kwd = {'expires_days': None}
        else:
            kwd = {}
        self.set_cookie('user', user, **kwd)
        self.set_secure_cookie('verify', user[::-1], **kwd)
        self.set_secure_cookie('type', str(type), **kwd)

    def safe_redirect(self, url):
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
        self.clear_cookie("name")
        self.clear_cookie("user")
        self.clear_cookie('type')

    def is_ajax(self):
        return (self.request.headers.get('X-Requested-With', None)
                == "XMLHttpRequest")

    @property
    def db(self):    # lazy-load
        return self.application.settings['db']

    # def get_user_locale(self):
        # todo: able to change
        # return tornado.locale.get('zh_CN')

    def write_error(self, status_code, **kwargs):
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
