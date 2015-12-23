import logging
try:
    from urllib.parse import urlunsplit
except ImportError:
    from urlparse import urlunsplit

import sys
import os
sys.path.insert(0, os.path.normpath(os.path.join(__file__,
                                                 '..', '..', '..', '..')))
from lib.hdlr.base import BaseHandler, EnsureSsl
from lib.tool.tracemore import get_exc_plus
sys.path.pop(0)

logger = logging.getLogger('tomorrow.utiltiy.sina.base')


class BaseHandler(BaseHandler):

    def check_xsrf_cookie(self):
        return True

    def set_app(self, key, secret):
        self.set_secure_cookie('app-key', key, expires_days=None)
        self.set_secure_cookie('app-secret', secret, expires_days=None)

    def get_app(self):
        key = self.get_secure_cookie('app-key')
        if key is None:
            return None, None

        key = key.decode('utf-8')
        secret = self.get_secure_cookie('app-secret').decode('utf-8')
        return (key, secret)

    def set_auth(self, token, expire):
        self.set_secure_cookie('auth-token', token, expires_days=None)
        self.set_secure_cookie('auth-expire', str(expire), expires_days=None)

    def get_auth(self):
        token = self.get_secure_cookie('auth-token')
        if token is None:
            return None, None

        token = token.decode('utf-8')
        expire = int(self.get_secure_cookie('auth-expire'))
        return token, expire

    @property
    def callback_url(self):
        request = self.request
        host = request.host
        protocol = request.protocol
        split_result = (protocol, host, '/utility/sina/callback/', '', '')
        return urlunsplit(split_result)

    def write_error(self, status_code, **kwargs):
        logging.info('%s' % get_exc_plus())
        err, ins, trace = kwargs['exc_info']
        message = str(ins)
        return self.render(
            'utility/sina/error.html',
            code=status_code,
            message=message
        )