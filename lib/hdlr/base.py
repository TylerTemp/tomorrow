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

    @property
    def db(self):    # lazy-load
        return self.application.settings['db']

    def get_user_locale(self):
        # todo: able to change
        return tornado.locale.get('zh_CN')

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
