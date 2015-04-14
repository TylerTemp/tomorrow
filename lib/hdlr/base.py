'''The basic handler of all tornado request
provide some convenient methods'''
import tornado.web
import logging

import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.tracemore import get_exc_plus
sys.path.pop(0)


class BaseHandler(tornado.web.RequestHandler):

    def initialize(self):
        self.DEBUG = self.application.settings['debug']

    def write_error(self, status_code, **kwargs):
        if self.DEBUG:
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
