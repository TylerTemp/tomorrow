'''The basic handler of all tornado request
provide some convenient methods'''
import tornado.web
import logging

import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.tool.tracemore import get_exc_plus
sys.path.pop(0)

logger = logging.getLogger("base")


class BaseHandler(tornado.web.RequestHandler):

    def get_current_user(self):
        name = self.get_cookie("name")
        user = self.get_secure_cookie("user")
        level = self.get_secure_cookie('type')
        if user is None:
            return None
        user = user.decode('utf-8')[::-1]
        if user != name:
            return None
        return {'user': name, 'type': int(level)}

    def set_user(self, user, type, temp=False):
        if temp:
            kwd = {'expires_days': None}
        else:
            kwd = {}
        self.set_cookie('name', user, **kwd)
        self.set_secure_cookie('user', user[::-1], **kwd)
        self.set_secure_cookie('type', str(type), **kwd)

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

        if status_code == 404:
            return self.render('404.html')
        else:
            logging.error('%s' % get_exc_plus())
            # uncomment this line for py2
            # return self.__class__.write_error(self, status_code, **kwargs)
            # uncomment this line for py3
            return super(BaseHandler, self).write_error(status_code, **kwargs)
