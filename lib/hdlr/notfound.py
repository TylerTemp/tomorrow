import tornado.web
import logging
try:
    from urllib.parse import urlsplit
    from urllib.parse import urlunsplit
except ImportError:
    from urlparse import urlsplit
    from urlparse import urlunsplit

import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.hdlr.base import BaseHandler
sys.path.pop(0)

logger = logging.getLogger('tomorrow.404')


class AddSlashOr404Handler(BaseHandler):

    def get(self):
        splited = urlsplit(self.request.uri)
        if not splited.path.endswith('/'):
            to_list = list(splited)
            to_list[2] = splited.path + '/'
            return self.redirect(urlunsplit(to_list), True)
        self.clear()
        self.set_status(404)
        return self.render('404.html')
